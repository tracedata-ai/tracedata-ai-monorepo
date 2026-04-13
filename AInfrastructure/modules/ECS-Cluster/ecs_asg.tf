# ---------------------------------------------------------------------------
# Data source — resolves the latest Amazon ECS-optimised AMI (Amazon Linux
# 2023) from SSM Parameter Store at plan time.  No hardcoded AMI IDs needed.
# ---------------------------------------------------------------------------
data "aws_ssm_parameter" "ecs_ami" {
  name = "/aws/service/ecs/optimized-ami/amazon-linux-2023/recommended/image_id"
}

# ---------------------------------------------------------------------------
# Launch Template — defines every configuration option for EC2 instances
# that the Auto Scaling Group will launch into the ECS cluster.
#
# Key decisions:
#   key_name = null → no SSH key pair; access via SSM Session Manager only
#   http_tokens = "required" → IMDSv2 enforced for container metadata security
#   http_put_response_hop_limit = 2 → required so containers can reach IMDS
#   encrypted = true → EBS root volume is encrypted at rest
# ---------------------------------------------------------------------------
resource "aws_launch_template" "ecs" {
  name_prefix   = "${var.project_name}-${var.environment}-ecs-lt-"
  image_id      = data.aws_ssm_parameter.ecs_ami.value
  instance_type = var.ecs_instance_type

  # No key_name — SSM Session Manager is used for shell access instead of SSH
  key_name = null

  # Attach the ECS instance profile so the host can join the cluster
  iam_instance_profile {
    arn = aws_iam_instance_profile.ecs_instance_profile.arn
  }

  # Place instances in the backend SG (already allows egress to 0.0.0.0/0
  # via NAT Gateway; additional dynamic-port ingress is added in backend_sg.tf)
  vpc_security_group_ids = [var.backend_sg_id]

  # Registers the instance with the ECS cluster and installs the SSM agent
  user_data = base64encode(templatefile("${path.module}/userdata.sh", {
    cluster_name = aws_ecs_cluster.this.name
  }))

  # Detailed (1-minute) CloudWatch monitoring for EC2 metrics
  monitoring {
    enabled = true
  }

  # IMDSv2 required — prevents SSRF attacks from reaching the metadata endpoint
  # hop_limit = 2 is needed so containers can access task-level IAM credentials
  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 2
  }

  # 30 GB encrypted gp3 root volume — sufficient for ECS agent + Docker images
  block_device_mappings {
    device_name = "/dev/xvda"
    ebs {
      volume_size           = 30
      volume_type           = "gp3"
      delete_on_termination = true
      encrypted             = true
    }
  }

  # Tag each EC2 instance launched from this template
  tag_specifications {
    resource_type = "instance"
    tags = merge(local.common_tags, {
      Name = "${var.project_name}-${var.environment}-ecs-instance"
    })
  }

  tags = local.common_tags
}

# ---------------------------------------------------------------------------
# Auto Scaling Group — spans BOTH private subnets for AZ redundancy.
# Uses a mixed_instances_policy so the override can be expanded to spot
# instances in the future without changing the launch template.
#
# protect_from_scale_in = true is REQUIRED when using ECS managed termination
# protection. The capacity provider will only terminate an instance after ECS
# has drained all running tasks from it; without this flag the
# CreateCapacityProvider API call returns HTTP 400.
# ---------------------------------------------------------------------------
resource "aws_autoscaling_group" "ecs" {
  name                      = "${var.project_name}-${var.environment}-ecs-asg"
  vpc_zone_identifier       = var.private_subnet_ids
  min_size                  = var.ecs_min_instances
  max_size                  = var.ecs_max_instances
  desired_capacity          = var.ecs_desired_instances
  health_check_type         = "EC2"
  health_check_grace_period = 300
  protect_from_scale_in     = true # required for ECS managed termination protection

  # Rolling replacement: wait for 100% healthy before removing old instance
  instance_maintenance_policy {
    min_healthy_percentage = 100
    max_healthy_percentage = 200
  }

  # Mixed instances policy — on-demand only for now; change to add spot later
  mixed_instances_policy {
    instances_distribution {
      on_demand_base_capacity                  = 1   # first instance is always on-demand
      on_demand_percentage_above_base_capacity = 100 # all additional instances are on-demand
    }

    launch_template {
      launch_template_specification {
        launch_template_id = aws_launch_template.ecs.id
        version            = "$Latest"
      }

      # Override with the chosen instance type (change here to add more types)
      override {
        instance_type = var.ecs_instance_type
      }
    }
  }

  # Required tag so ECS capacity provider can manage this ASG's instances
  tag {
    key                 = "AmazonECSManaged"
    value               = true
    propagate_at_launch = true
  }
}
