# ---------------------------------------------------------------------------
# Root main.tf — calls the VPC module with all required input variables.
# All concrete values are supplied via terraform.tfvars.
# ---------------------------------------------------------------------------
module "vpc" {
  source = "./modules/VPC"

  # Naming / tagging
  project_name = var.project_name
  environment  = var.environment

  # Network addressing
  vpc_cidr             = var.vpc_cidr
  public_subnet_1_cidr = var.public_subnet_1_cidr
  public_subnet_2_cidr = var.public_subnet_2_cidr
  private_subnet_1_cidr = var.private_subnet_1_cidr
  private_subnet_2_cidr = var.private_subnet_2_cidr

  # Availability zone placement
  availability_zone_1 = var.availability_zone_1
  availability_zone_2 = var.availability_zone_2
}

# ---------------------------------------------------------------------------
# ALB module — internal Application Load Balancer deployed in private subnets.
# VPC outputs are wired directly so no hardcoded IDs are needed here.
# ---------------------------------------------------------------------------
module "alb" {
  source = "./modules/ALB"

  # Naming / tagging
  project_name = var.project_name
  environment  = var.environment

  # Network context from the VPC module
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  vpc_cidr           = var.vpc_cidr

  # ALB-specific settings
  alb_name                   = var.alb_name
  target_group_name          = var.target_group_name
  health_check_path          = var.health_check_path
  target_type                = var.target_type
  enable_deletion_protection = var.enable_deletion_protection
}

# ---------------------------------------------------------------------------
# API Gateway module - HTTP API + VPC Link V2 + backend SG.
# Wires directly to VPC and ALB module outputs; no hardcoded IDs.
# ---------------------------------------------------------------------------
module "api_gateway" {
  source = "./modules/API-Gateway"

  # Naming / tagging
  project_name = var.project_name
  environment  = var.environment

  # Network context from the VPC module
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids

  # ALB context from the ALB module
  alb_dns_name     = module.alb.alb_dns_name
  alb_sg_id        = module.alb.alb_sg_id
  alb_listener_arn = module.alb.http_listener_arn

  # API Gateway-specific settings
  api_gateway_name = var.api_gateway_name
  api_stage_name   = var.api_stage_name
  vpc_link_name    = var.vpc_link_name
}

# ---------------------------------------------------------------------------
# ECS Cluster module — EC2 launch type cluster with Auto Scaling, capacity
# provider, IAM roles, task definition, and service.
# Wires directly to VPC, ALB, and API-Gateway module outputs; no hardcoded IDs.
# ---------------------------------------------------------------------------
module "ecs_cluster" {
  source = "./modules/ECS-Cluster"

  # Naming / tagging
  project_name = var.project_name
  environment  = var.environment
  aws_region   = var.aws_region

  # Network context from the VPC module
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids

  # ALB context — use EXISTING target group and security group (no new ones)
  target_group_arn = module.alb.target_group_arn
  alb_sg_id        = module.alb.alb_sg_id

  # Backend SG from the API-Gateway module — ECS instances use this SG
  backend_sg_id = module.api_gateway.backend_sg_id

  # EC2 / ASG sizing
  ecs_instance_type     = var.ecs_instance_type
  ecs_min_instances     = var.ecs_min_instances
  ecs_max_instances     = var.ecs_max_instances
  ecs_desired_instances = var.ecs_desired_instances

  # ECS service sizing
  service_replica_count = var.service_replica_count

  # Container configuration
  container_name  = var.container_name
  container_image = var.container_image
  container_port  = var.container_port

  # Task resource limits
  task_cpu    = var.task_cpu
  task_memory = var.task_memory

  # Container-level resource limits (independent from task-level ceilings)
  container_cpu                = var.container_cpu
  container_memory             = var.container_memory
  container_memory_reservation = var.container_memory_reservation

  # Next.js runtime environment variables
  node_env     = var.node_env
  node_options = var.node_options

  # Observability
  log_retention_days = var.log_retention_days
}
