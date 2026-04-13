# ---------------------------------------------------------------------------
# Passed in from the root module / VPC module outputs
# ---------------------------------------------------------------------------

variable "project_name" {
  type        = string
  description = "Project name used as a prefix in resource Name tags"
}

variable "environment" {
  type        = string
  description = "Deployment environment (e.g. dev, staging, prod)"
}

variable "vpc_id" {
  type        = string
  description = "ID of the VPC in which the ALB and security group are created"
}

variable "private_subnet_ids" {
  type        = list(string)
  description = "List of private subnet IDs across which the internal ALB is deployed"
}

variable "vpc_cidr" {
  type        = string
  description = "VPC CIDR block — used to scope SG inbound and outbound rules to the VPC only"
}

# ---------------------------------------------------------------------------
# ALB-specific configuration
# ---------------------------------------------------------------------------

variable "alb_name" {
  type        = string
  description = "Name of the Application Load Balancer (max 32 characters)"
}

variable "target_group_name" {
  type        = string
  description = "Name of the target group (max 32 characters)"
}

variable "health_check_path" {
  type        = string
  description = "HTTP path used for target group health checks"
  default     = "/health"
}

variable "target_type" {
  type        = string
  description = "Target group target type: \"ip\" (ECS/Fargate) or \"instance\" (EC2)"
  default     = "ip"

  validation {
    condition     = contains(["ip", "instance", "lambda"], var.target_type)
    error_message = "target_type must be one of: ip, instance, lambda."
  }
}

variable "enable_deletion_protection" {
  type        = bool
  description = "Set to true to prevent accidental deletion of the ALB (recommended for prod)"
  default     = false
}

variable "deregistration_delay" {
  type        = number
  description = "Seconds the ALB waits before deregistering a draining target (AWS default is 300; use 30 for non-prod to speed up deployments and destroys)"
  default     = 30
}
