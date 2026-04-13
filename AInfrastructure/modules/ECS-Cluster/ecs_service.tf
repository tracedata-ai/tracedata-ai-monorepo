# ---------------------------------------------------------------------------
# ECS Service — runs and maintains var.service_replica_count tasks on the
# EC2 cluster defined above.
#
# capacity_provider_strategy is used instead of launch_type = "EC2" because
# the cluster uses a managed capacity provider.  Both approaches schedule on
# EC2, but the strategy approach is required when capacity providers are active.
#
# load_balancer block wires the service to the EXISTING ALB target group.
# ECS registers the EC2 instance + dynamic hostPort as a target automatically.
#
# deployment_circuit_breaker rolls back to the previous task definition if
# the new deployment fails to become healthy within the grace period.
# ---------------------------------------------------------------------------
resource "aws_ecs_service" "this" {
  name            = "${var.project_name}-${var.environment}-frontend-svc"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.this.arn
  desired_count   = var.service_replica_count

  # Use the capacity provider instead of a fixed launch_type declaration
  capacity_provider_strategy {
    capacity_provider = aws_ecs_capacity_provider.this.name
    base              = 1   # ensure at least 1 task runs on this provider
    weight            = 100 # all tasks go to this provider
  }

  # Wire to the EXISTING ALB target group — do NOT create a new target group
  load_balancer {
    target_group_arn = var.target_group_arn
    container_name   = var.container_name
    container_port   = var.container_port
  }

  # Force immediate deletion on destroy — skips the full ALB deregistration drain
  # so "terraform destroy" completes in seconds instead of 5+ minutes.
  force_delete = true

  # Allow rolling deployments: tolerate down to 50% healthy tasks during deploy
  deployment_minimum_healthy_percent = 50
  deployment_maximum_percent         = 200

  # Auto-rollback if the new task set fails to stabilise
  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  # Ensure the capacity provider is ready and IAM policies are attached before
  # the service tries to launch tasks or register targets with the ALB
  depends_on = [
    aws_ecs_capacity_provider.this,
    aws_iam_role_policy_attachment.ecs_task_role_admin,
    aws_iam_role_policy_attachment.task_execution_ecs,
  ]
}
