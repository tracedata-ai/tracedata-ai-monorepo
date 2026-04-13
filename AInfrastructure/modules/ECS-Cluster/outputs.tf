output "ecs_cluster_id" {
  description = "ID of the ECS cluster"
  value       = aws_ecs_cluster.this.id
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.this.name
}

output "ecs_service_name" {
  description = "Name of the ECS service"
  value       = aws_ecs_service.this.name
}

output "ecs_task_definition_arn" {
  description = "Full ARN of the ECS task definition (including revision)"
  value       = aws_ecs_task_definition.this.arn
}

output "ecs_asg_name" {
  description = "Name of the Auto Scaling Group backing the ECS cluster"
  value       = aws_autoscaling_group.ecs.name
}

output "ecs_capacity_provider" {
  description = "Name of the ECS capacity provider linked to the ASG"
  value       = aws_ecs_capacity_provider.this.name
}

output "cloudwatch_log_group" {
  description = "Name of the CloudWatch Log Group that receives container logs"
  value       = aws_cloudwatch_log_group.ecs.name
}

output "ecs_instance_role_arn" {
  description = "ARN of the IAM role attached to ECS EC2 instance profiles"
  value       = aws_iam_role.ecs_instance_role.arn
}

output "ecs_task_role_arn" {
  description = "ARN of the IAM role assumed by the running application container"
  value       = aws_iam_role.ecs_task_role.arn
}

output "ecs_task_execution_role_arn" {
  description = "ARN of the IAM role used by ECS to pull images and write logs"
  value       = aws_iam_role.ecs_task_execution_role.arn
}
