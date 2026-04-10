output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "internet_gateway_id" {
  description = "ID of the Internet Gateway"
  value       = module.vpc.internet_gateway_id
}

output "nat_gateway_id" {
  description = "ID of the NAT Gateway"
  value       = module.vpc.nat_gateway_id
}

output "nat_gateway_public_ip" {
  description = "Public Elastic IP address of the NAT Gateway"
  value       = module.vpc.nat_gateway_public_ip
}

output "public_subnet_ids" {
  description = "List of both public subnet IDs"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "List of both private subnet IDs"
  value       = module.vpc.private_subnet_ids
}

output "public_route_table_id" {
  description = "ID of the public route table"
  value       = module.vpc.public_route_table_id
}

output "private_route_table_id" {
  description = "ID of the private route table"
  value       = module.vpc.private_route_table_id
}

# ---------------------------------------------------------------------------
# ALB outputs
# ---------------------------------------------------------------------------

output "alb_arn" {
  description = "Full ARN of the internal Application Load Balancer"
  value       = module.alb.alb_arn
}

output "alb_dns_name" {
  description = "DNS name of the ALB (used by VPC Link or Route 53 records)"
  value       = module.alb.alb_dns_name
}

output "alb_zone_id" {
  description = "Canonical hosted zone ID of the ALB (for Route 53 alias records)"
  value       = module.alb.alb_zone_id
}

output "alb_sg_id" {
  description = "Security group ID attached to the internal ALB"
  value       = module.alb.alb_sg_id
}

output "target_group_arn" {
  description = "ARN of the target group"
  value       = module.alb.target_group_arn
}

output "http_listener_arn" {
  description = "ARN of the HTTP (port 80) listener"
  value       = module.alb.http_listener_arn
}

# ---------------------------------------------------------------------------
# API Gateway outputs
# ---------------------------------------------------------------------------

output "api_gateway_id" {
  description = "HTTP API ID"
  value       = module.api_gateway.api_gateway_id
}

output "api_gateway_invoke_url" {
  description = "Full invoke URL including the stage name (e.g. .../uat/)"
  value       = module.api_gateway.api_gateway_invoke_url
}

output "api_gateway_default_invoke_url" {
  description = "$default stage invoke URL — no stage prefix required"
  value       = module.api_gateway.api_gateway_default_invoke_url
}

output "api_gateway_stage_name" {
  description = "Name of the deployed stage"
  value       = module.api_gateway.api_gateway_stage_name
}

output "vpc_link_id" {
  description = "ID of the VPC Link V2"
  value       = module.api_gateway.vpc_link_id
}

output "vpc_link_sg_id" {
  description = "Security group ID attached to the VPC Link"
  value       = module.api_gateway.vpc_link_sg_id
}

output "backend_sg_id" {
  description = "Security group ID for backend compute resources"
  value       = module.api_gateway.backend_sg_id
}

output "api_gateway_proxy_route_id" {
  description = "Route ID for ANY /{proxy+}"
  value       = module.api_gateway.api_gateway_proxy_route_id
}

output "api_gateway_root_route_id" {
  description = "Route ID for ANY /"
  value       = module.api_gateway.api_gateway_root_route_id
}

# ---------------------------------------------------------------------------
# ECS Cluster outputs
# ---------------------------------------------------------------------------

output "ecs_cluster_id" {
  description = "ID of the ECS cluster"
  value       = module.ecs_cluster.ecs_cluster_id
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = module.ecs_cluster.ecs_cluster_name
}

output "ecs_service_name" {
  description = "Name of the ECS service"
  value       = module.ecs_cluster.ecs_service_name
}

output "ecs_task_definition_arn" {
  description = "Full ARN of the ECS task definition (including revision)"
  value       = module.ecs_cluster.ecs_task_definition_arn
}

output "ecs_asg_name" {
  description = "Name of the Auto Scaling Group backing the ECS cluster"
  value       = module.ecs_cluster.ecs_asg_name
}

output "ecs_capacity_provider" {
  description = "Name of the ECS capacity provider linked to the ASG"
  value       = module.ecs_cluster.ecs_capacity_provider
}

output "cloudwatch_log_group" {
  description = "Name of the CloudWatch Log Group that receives container logs"
  value       = module.ecs_cluster.cloudwatch_log_group
}

output "ecs_instance_role_arn" {
  description = "ARN of the IAM role attached to ECS EC2 instance profiles"
  value       = module.ecs_cluster.ecs_instance_role_arn
}

output "ecs_task_role_arn" {
  description = "ARN of the IAM role assumed by the running application container"
  value       = module.ecs_cluster.ecs_task_role_arn
}

output "ecs_task_execution_role_arn" {
  description = "ARN of the IAM role used by ECS to pull images and write logs"
  value       = module.ecs_cluster.ecs_task_execution_role_arn
}
