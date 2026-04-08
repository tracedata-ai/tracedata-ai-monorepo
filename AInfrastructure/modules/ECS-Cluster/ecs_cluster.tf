# ---------------------------------------------------------------------------
# locals — shared tags applied to every resource to avoid repetition.
# All ECS module resources inherit these via merge(local.common_tags, {...})
# ---------------------------------------------------------------------------
locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# ---------------------------------------------------------------------------
# ECS Cluster — EC2 launch type cluster with CloudWatch Container Insights.
# Container Insights publishes per-task CPU, memory, and network metrics
# to CloudWatch at the cluster level.
# ---------------------------------------------------------------------------
resource "aws_ecs_cluster" "this" {
  name = "${var.project_name}-${var.environment}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = local.common_tags
}

# ---------------------------------------------------------------------------
# ECS Capacity Provider — links the Auto Scaling Group to this ECS cluster.
# Managed scaling automatically adjusts ASG capacity based on ECS workload.
# managed_termination_protection prevents ASG from terminating instances
# that still have running tasks.
# ---------------------------------------------------------------------------
resource "aws_ecs_capacity_provider" "this" {
  name = "${var.project_name}-${var.environment}-cp"

  auto_scaling_group_provider {
    auto_scaling_group_arn         = aws_autoscaling_group.ecs.arn
    managed_termination_protection = "ENABLED"

    managed_scaling {
      maximum_scaling_step_size = 3
      minimum_scaling_step_size = 1
      status                    = "ENABLED"
      target_capacity           = 80 # scale up when cluster reservation exceeds 80%
    }
  }
}

# ---------------------------------------------------------------------------
# Cluster Capacity Provider Association — binds the capacity provider to the
# cluster and sets it as the default strategy for all services that do not
# specify an explicit capacity provider.
# ---------------------------------------------------------------------------
resource "aws_ecs_cluster_capacity_providers" "this" {
  cluster_name       = aws_ecs_cluster.this.name
  capacity_providers = [aws_ecs_capacity_provider.this.name]

  default_capacity_provider_strategy {
    capacity_provider = aws_ecs_capacity_provider.this.name
    base              = 1   # always keep at least 1 task on this provider
    weight            = 100 # 100% of tasks use this provider
  }
}
