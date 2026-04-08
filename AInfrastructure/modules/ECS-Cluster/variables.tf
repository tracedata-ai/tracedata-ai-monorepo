# ---------------------------------------------------------------------------
# Shared naming / tagging (passed from root module)
# ---------------------------------------------------------------------------

variable "project_name" {
  type        = string
  description = "Project name used as a prefix in resource Name tags"
}

variable "environment" {
  type        = string
  description = "Deployment environment (e.g. dev, staging, prod)"
}

variable "aws_region" {
  type        = string
  description = "AWS region — used in CloudWatch Logs configuration for the container"
}

# ---------------------------------------------------------------------------
# Network context (from VPC module outputs)
# ---------------------------------------------------------------------------

variable "vpc_id" {
  type        = string
  description = "ID of the VPC in which all ECS resources are deployed"
}

variable "private_subnet_ids" {
  type        = list(string)
  description = "List of both private subnet IDs — ECS EC2 instances are placed here"
}

# ---------------------------------------------------------------------------
# ALB / SG context (from ALB and API-Gateway module outputs)
# ---------------------------------------------------------------------------

variable "target_group_arn" {
  type        = string
  description = "ARN of the EXISTING ALB target group — ECS registers dynamic ports here"
}

variable "alb_sg_id" {
  type        = string
  description = "Security group ID of the internal ALB — used for dynamic-port egress rule"
}

variable "backend_sg_id" {
  type        = string
  description = "Security group ID for backend EC2 instances — used for dynamic-port ingress rule"
}

# ---------------------------------------------------------------------------
# EC2 / ASG sizing
# ---------------------------------------------------------------------------

variable "ecs_instance_type" {
  type        = string
  description = "EC2 instance type for ECS container instances (must be Intel x86_64)"
  default     = "c7i-flex.large"
}

variable "ecs_min_instances" {
  type        = number
  description = "Minimum number of EC2 instances in the Auto Scaling Group"
  default     = 1
}

variable "ecs_max_instances" {
  type        = number
  description = "Maximum number of EC2 instances in the Auto Scaling Group"
  default     = 3
}

variable "ecs_desired_instances" {
  type        = number
  description = "Initial desired number of EC2 instances in the Auto Scaling Group"
  default     = 1
}

# ---------------------------------------------------------------------------
# ECS service sizing
# ---------------------------------------------------------------------------

variable "service_replica_count" {
  type        = number
  description = "Desired number of running ECS task replicas (containers)"
  default     = 1
}

# ---------------------------------------------------------------------------
# Container configuration
# ---------------------------------------------------------------------------

variable "container_name" {
  type        = string
  description = "Name of the container as defined in the ECS task definition"
}

variable "container_image" {
  type        = string
  description = "Full ECR image URI with tag (e.g. 123456789.dkr.ecr.ap-southeast-1.amazonaws.com/myapp:latest)"
}

variable "container_port" {
  type        = number
  description = "Port the application listens on inside the container (Next.js default: 3000)"
  default     = 3000
}

# ---------------------------------------------------------------------------
# Task resource limits
# ---------------------------------------------------------------------------

variable "task_cpu" {
  type        = string
  description = "Task-level CPU units allocated to the entire task (hard ceiling)"
  default     = "1024"
}

variable "task_memory" {
  type        = string
  description = "Task-level memory in MB allocated to the entire task (hard ceiling)"
  default     = "2048"
}

variable "container_cpu" {
  type        = number
  description = "CPU units reserved for the container (relative share within the task)"
  default     = 1024
}

variable "container_memory" {
  type        = number
  description = "Hard memory limit for the container in MB — container is OOM-killed if exceeded"
  default     = 2048
}

variable "container_memory_reservation" {
  type        = number
  description = "Soft memory limit used for task placement in MB — container may burst above this"
  default     = 1024
}

variable "node_env" {
  type        = string
  description = "Value for the NODE_ENV environment variable inside the container"
  default     = "production"
}

variable "node_options" {
  type        = string
  description = "Value for the NODE_OPTIONS environment variable — used to tune the V8 heap size"
  default     = "--max-old-space-size=1536"
}

# ---------------------------------------------------------------------------
# Observability
# ---------------------------------------------------------------------------

variable "log_retention_days" {
  type        = number
  description = "Number of days to retain container logs in CloudWatch Logs"
  default     = 7
}
