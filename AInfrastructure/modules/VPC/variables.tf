variable "project_name" {
  type        = string
  description = "Project name used in resource Name tags and prefixes"
}

variable "environment" {
  type        = string
  description = "Environment name (e.g. dev, staging, prod)"
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for the VPC (e.g. 10.0.0.0/16)"
}

variable "public_subnet_1_cidr" {
  type        = string
  description = "CIDR block for public subnet 1"
}

variable "public_subnet_2_cidr" {
  type        = string
  description = "CIDR block for public subnet 2"
}

variable "private_subnet_1_cidr" {
  type        = string
  description = "CIDR block for private subnet 1"
}

variable "private_subnet_2_cidr" {
  type        = string
  description = "CIDR block for private subnet 2"
}

variable "availability_zone_1" {
  type        = string
  description = "First availability zone for subnet placement (e.g. us-east-1a)"
}

variable "availability_zone_2" {
  type        = string
  description = "Second availability zone for subnet placement (e.g. us-east-1b)"
}