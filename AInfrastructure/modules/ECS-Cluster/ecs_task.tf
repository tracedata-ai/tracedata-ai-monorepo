# ---------------------------------------------------------------------------
# CloudWatch Log Group — receives container stdout/stderr via awslogs driver.
# retention_in_days prevents unbounded log accumulation and controls cost.
# awslogs-create-group = "true" in the container log config means ECS will
# auto-create this group if it doesn't exist yet, but the explicit resource
# here ensures Terraform owns the lifecycle (retention, tags, deletion).
# ---------------------------------------------------------------------------
resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/${var.project_name}-${var.environment}"
  retention_in_days = var.log_retention_days

  tags = local.common_tags
}

# ---------------------------------------------------------------------------
# ECS Task Definition — describes the container, resource limits, and the
# two IAM roles that ECS requires:
#
#   execution_role_arn → used by the ECS AGENT to pull the image and write logs
#   task_role_arn      → used by the RUNNING CONTAINER to call AWS services
#
# network_mode = "bridge" is required for EC2 launch type with dynamic port
# mapping (hostPort = 0).  "awsvpc" is only supported on Fargate or when
# you manage ENIs per task, which is not the case here.
#
# hostPort = 0 → ECS assigns a random ephemeral port on the EC2 host and
# registers that port with the ALB target group automatically.
#
# Container-level cpu/memory are set independently from the task-level limits:
#   task cpu/memory  = hard ceiling enforced by ECS on the entire task
#   container cpu    = relative CPU share within the task
#   container memory = hard limit per container (OOM kill if exceeded)
#   memoryReservation= soft limit — used for scheduling; container can burst
# ---------------------------------------------------------------------------
resource "aws_ecs_task_definition" "this" {
  family                   = "${var.project_name}-${var.environment}-task"
  network_mode             = "bridge"
  requires_compatibilities = ["EC2"]
  cpu                      = var.task_cpu
  memory                   = var.task_memory

  # Role the CONTAINER uses to call AWS services at runtime.
  # ⚠️  AdministratorAccess is used for dev — scope down to least-privilege for production.
  task_role_arn = aws_iam_role.ecs_task_role.arn

  # Role ECS uses to pull the ECR image and write CloudWatch Logs
  execution_role_arn = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([{
    name              = var.container_name
    image             = var.container_image
    cpu               = var.container_cpu               # CPU units reserved for this container
    memory            = var.container_memory            # hard memory limit (OOM kill threshold)
    memoryReservation = var.container_memory_reservation # soft limit used for task placement

    # containerPort = Next.js port inside the container
    # hostPort = 0   → dynamic assignment; ECS picks a free ephemeral port on the EC2 host
    portMappings = [{
      containerPort = var.container_port
      hostPort      = 0 # 0 = dynamic port mapping — ALB discovers the assigned port via target registration
      protocol      = "tcp"
    }]

    # Runtime environment variables injected into the Next.js process
    environment = [
      {
        name  = "NODE_OPTIONS"
        value = var.node_options # e.g. "--max-old-space-size=1536" — prevents V8 heap OOM
      },
      {
        name  = "NODE_ENV"
        value = var.node_env # "production" enables Next.js optimisations
      }
    ]

    # Container-level health check — ECS marks task (un)healthy independently
    # of the ALB health check.  Uses wget because curl is not in the base image.
    # startPeriod = 60s gives Next.js time to finish cold-start compilation before
    # the first check fires.
    healthCheck = {
      command     = ["CMD-SHELL", "wget -qO- http://127.0.0.1:${var.container_port}/health || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 60
    }

    # awslogs driver streams container stdout/stderr to the CloudWatch log group
    # awslogs-create-group = "true" auto-creates the group if it doesn't exist yet;
    # the aws_cloudwatch_log_group resource above is still the authoritative owner.
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/ecs/${var.project_name}-${var.environment}"
        "awslogs-create-group"  = "true"
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }

    mountPoints    = []
    volumesFrom    = []
    systemControls = []
    essential      = true # ECS stops the task if this container exits
  }])

  tags = local.common_tags
}
