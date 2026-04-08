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

# ---------------------------------------------------------------------------
# Network context (from VPC module outputs)
# ---------------------------------------------------------------------------

variable "vpc_id" {
  type        = string
  description = "ID of the VPC in which all resources are created"
}

variable "private_subnet_ids" {
  type        = list(string)
  description = "List of both private subnet IDs used for VPC Link attachment"
}

# ---------------------------------------------------------------------------
# ALB context (from ALB module outputs)
# ---------------------------------------------------------------------------

variable "alb_dns_name" {
  type        = string
  description = "DNS name of the internal ALB (used for reference/documentation)"
}

variable "alb_listener_arn" {
  type        = string
  description = "ARN of the ALB HTTP listener (port 80) — required as integration_uri for HTTP API + VPC_LINK"
}

variable "alb_sg_id" {
  type        = string
  description = "Security group ID of the internal ALB (for VPC Link SG egress and backend SG ingress)"
}

# ---------------------------------------------------------------------------
# API Gateway settings
# ---------------------------------------------------------------------------

variable "api_gateway_name" {
  type        = string
  description = "Name for the API Gateway HTTP API"
}

variable "api_stage_name" {
  type        = string
  description = "Deployment stage name (e.g. dev, staging, prod)"
  default     = "dev"
}

variable "vpc_link_name" {
  type        = string
  description = "Name for the VPC Link V2 resource"
}
