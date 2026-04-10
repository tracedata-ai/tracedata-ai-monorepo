variable "aws_region" {
  type        = string
  description = "AWS region in which to create all resources (e.g. us-east-1)"
  default     = "us-east-1"
}

variable "project_name" {
  type        = string
  description = "Project name used as a prefix in resource Name tags"
  default     = "myapp"
}

variable "environment" {
  type        = string
  description = "Deployment environment — one of: dev, staging, prod"
  default     = "dev"
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for the VPC (e.g. 10.0.0.0/16)"
  default     = "10.0.0.0/16"
}

variable "public_subnet_1_cidr" {
  type        = string
  description = "CIDR block for public subnet 1 (must fall within vpc_cidr)"
  default     = "10.0.1.0/24"
}

variable "public_subnet_2_cidr" {
  type        = string
  description = "CIDR block for public subnet 2 (must fall within vpc_cidr)"
  default     = "10.0.2.0/24"
}

variable "private_subnet_1_cidr" {
  type        = string
  description = "CIDR block for private subnet 1 (must fall within vpc_cidr)"
  default     = "10.0.3.0/24"
}

variable "private_subnet_2_cidr" {
  type        = string
  description = "CIDR block for private subnet 2 (must fall within vpc_cidr)"
  default     = "10.0.4.0/24"
}

variable "availability_zone_1" {
  type        = string
  description = "First availability zone for subnet placement (e.g. us-east-1a)"
  default     = "us-east-1a"
}

variable "availability_zone_2" {
  type        = string
  description = "Second availability zone for subnet placement (e.g. us-east-1b)"
  default     = "us-east-1b"
}

# ---------------------------------------------------------------------------
# ALB variables
# ---------------------------------------------------------------------------

variable "alb_name" {
  type        = string
  description = "Name of the internal Application Load Balancer (max 32 characters)"
  default     = "internal-alb"
}

variable "target_group_name" {
  type        = string
  description = "Name of the ALB target group (max 32 characters)"
  default     = "app-tg"
}

variable "health_check_path" {
  type        = string
  description = "HTTP path the ALB uses for target health checks"
  default     = "/health"
}

variable "target_type" {
  type        = string
  description = "Target group target type: \"ip\" (ECS/Fargate) or \"instance\" (EC2)"
  default     = "ip"
}

variable "enable_deletion_protection" {
  type        = bool
  description = "Prevent accidental deletion of the ALB (set to true for prod)"
  default     = false
}

# ---------------------------------------------------------------------------
# API Gateway variables
# ---------------------------------------------------------------------------

variable "api_gateway_name" {
  type        = string
  description = "Name for the API Gateway HTTP API"
  default     = "myapp-api"
}

variable "api_stage_name" {
  type        = string
  description = "Deployment stage name (e.g. dev, staging, prod)"
  default     = "dev"
}

variable "vpc_link_name" {
  type        = string
  description = "Name for the VPC Link V2 resource"
  default     = "myapp-vpc-link"
}

# ---------------------------------------------------------------------------
# ECS on EC2 variables
# ---------------------------------------------------------------------------

variable "ecs_instance_type" {
  type        = string
  description = "EC2 instance type for ECS container instances (must be Intel x86_64)"
  default     = "c7i-flex.large"
}

variable "ecs_min_instances" {
  type        = number
  description = "Minimum number of EC2 instances in the ECS Auto Scaling Group"
  default     = 1
}

variable "ecs_max_instances" {
  type        = number

  description = "Maximum number of EC2 instances in the ECS Auto Scaling Group"
  default     = 3
}

variable "ecs_desired_instances" {
  type        = number
  description = "Initial desired number of EC2 instances in the ECS Auto Scaling Group"
  default     = 1
}

variable "service_replica_count" {
  type        = number
  description = "Desired number of running ECS task replicas"
  default     = 1
}

variable "container_name" {
  type        = string
  description = "Name of the container as defined in the ECS task definition"
  default     = "frontend"
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

variable "log_retention_days" {
  type        = number
  description = "Number of days to retain container logs in CloudWatch Logs"
  default     = 7
}
