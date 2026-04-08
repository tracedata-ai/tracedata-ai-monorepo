# ---------------------------------------------------------------------------
# locals - shared tags applied to every taggable resource
# ---------------------------------------------------------------------------
locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# ---------------------------------------------------------------------------
# Security Group: VPC Link
# Inbound:  NONE - VPC Link does not receive inbound traffic
# Outbound: port 80 to ALB SG only - VPC Link can only talk to the ALB
# ---------------------------------------------------------------------------
resource "aws_security_group" "vpc_link_sg" {
  name        = "${var.project_name}-${var.environment}-vpclink-sg"
  description = "VPC Link SG - egress to ALB port 80 only"
  vpc_id      = var.vpc_id

  # No ingress rules - VPC Link only initiates outbound connections

  # Allow outbound HTTP to the ALB SG only - no 0.0.0.0/0 egress
  egress {
    description     = "HTTP to ALB SG"
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [var.alb_sg_id]
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-vpclink-sg"
  })
}

# ---------------------------------------------------------------------------
# ALB SG inbound rule - allow VPC Link to reach the ALB on port 80.
# Added to the existing ALB SG; keeps the existing VPC CIDR rule intact.
# ---------------------------------------------------------------------------
resource "aws_security_group_rule" "alb_allow_vpc_link" {
  type                     = "ingress"
  description              = "Allow HTTP from VPC Link SG"
  from_port                = 80
  to_port                  = 80
  protocol                 = "tcp"
  security_group_id        = var.alb_sg_id
  source_security_group_id = aws_security_group.vpc_link_sg.id
}

# ---------------------------------------------------------------------------
# VPC Link V2 - attaches API Gateway to both private subnets.
# Routes traffic privately to the internal ALB without needing an NLB.
# ---------------------------------------------------------------------------
resource "aws_apigatewayv2_vpc_link" "this" {
  name               = var.vpc_link_name
  subnet_ids         = var.private_subnet_ids
  security_group_ids = [aws_security_group.vpc_link_sg.id]

  tags = merge(local.common_tags, {
    Name = var.vpc_link_name
  })
}

# ---------------------------------------------------------------
# Request Flow:
# Client -> API Gateway HTTP API  (HTTPS - TLS terminates here)
#        -> VPC Link V2           (private, attached to private subnets)
#        -> Internal ALB          (HTTP port 80, private subnets)
#        -> Backend ECS/EC2       (HTTP port 80, private subnets)
#
# Key decisions:
# - HTTP API (aws_apigatewayv2_api) - simpler and cheaper than REST API
# - VPC Link V2 (aws_apigatewayv2_vpc_link) - no NLB required
# - No NLB - VPC Link V2 routes privately directly to ALB within the VPC
# - TLS terminates at API Gateway only - all internal traffic is HTTP port 80
# - TWO routes used:
#     ANY /{proxy+} - catches all paths with one or more segments
#     ANY /         - catches root path (/{proxy+} does NOT match /)
# - Both routes point to the same integration - all traffic reaches the ALB
# ---------------------------------------------------------------

# ---------------------------------------------------------------------------
# API Gateway HTTP API - receives HTTPS from clients; TLS terminates here.
# protocol_type = "HTTP" means HTTP API (v2), not REST API (v1).
# ---------------------------------------------------------------------------
resource "aws_apigatewayv2_api" "this" {
  name          = var.api_gateway_name
  protocol_type = "HTTP"

  tags = merge(local.common_tags, {
    Name = var.api_gateway_name
  })
}

# ---------------------------------------------------------------------------
# Integration - connects the HTTP API to the internal ALB via the VPC Link.
# integration_uri MUST be the ALB listener ARN when connection_type is
# VPC_LINK with an HTTP API - a DNS URL is only valid for REST API (v1).
# ---------------------------------------------------------------------------
resource "aws_apigatewayv2_integration" "this" {
  api_id                 = aws_apigatewayv2_api.this.id
  integration_type       = "HTTP_PROXY"
  integration_method     = "ANY"
  integration_uri        = var.alb_listener_arn
  connection_type        = "VPC_LINK"
  connection_id          = aws_apigatewayv2_vpc_link.this.id
  payload_format_version = "1.0"
}

# ---------------------------------------------------------------------------
# Route 1: ANY /{proxy+}
# Catches all paths with one or more segments: /users, /api/v1/products, etc.
# ---------------------------------------------------------------------------
resource "aws_apigatewayv2_route" "proxy" {
  api_id    = aws_apigatewayv2_api.this.id
  route_key = "ANY /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.this.id}"
}

# ---------------------------------------------------------------------------
# Route 2: ANY /
# Catches the root path - /{proxy+} alone does NOT match the root /.
# Both routes point to the same integration so all traffic reaches the ALB.
# ---------------------------------------------------------------------------
resource "aws_apigatewayv2_route" "root" {
  api_id    = aws_apigatewayv2_api.this.id
  route_key = "ANY /"
  target    = "integrations/${aws_apigatewayv2_integration.this.id}"
}

# ---------------------------------------------------------------------------
# Stage (named) - e.g. "uat". auto_deploy = true means changes deploy
# immediately; no separate aws_api_gateway_deployment resource is needed.
# Invoke URL: https://<api-id>.execute-api.<region>.amazonaws.com/uat/
# ---------------------------------------------------------------------------
resource "aws_apigatewayv2_stage" "this" {
  api_id      = aws_apigatewayv2_api.this.id
  name        = var.api_stage_name
  auto_deploy = true

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-${var.api_stage_name}"
  })
}

# ---------------------------------------------------------------------------
# $default stage - catches ALL requests that do not match a named stage.
# Invoke URL: https://<api-id>.execute-api.<region>.amazonaws.com/
# This is the recommended stage for HTTP APIs — no stage prefix in the URL
# so clients hit / directly without any /uat/ or /prod/ prefix.
# Both this stage and the named stage above share the same routes and
# integration, so either URL reaches the ALB and the ECS container.
# ---------------------------------------------------------------------------
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.this.id
  name        = "$default"
  auto_deploy = true

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-default"
  })
}

# ---------------------------------------------------------------------------
# Security Group: Backend compute (ECS/EC2 in private subnet)
# Inbound:  port 80 from ALB SG only - only the ALB can reach the backend
# Outbound: all traffic to 0.0.0.0/0 for external calls via NAT Gateway
# ---------------------------------------------------------------------------
resource "aws_security_group" "backend_sg" {
  name        = "${var.project_name}-${var.environment}-backend-sg"
  description = "Backend compute SG - allow HTTP from ALB SG only"
  vpc_id      = var.vpc_id

  # Allow all TCP from the ALB SG — ECS uses dynamic port mapping so the host
  # port is ephemeral (e.g. 32768+).  The ALB health-check and forwarding must
  # reach whatever port ECS registers, so the full TCP range is required.
  ingress {
    description     = "All TCP from ALB SG (dynamic port mapping)"
    from_port       = 0
    to_port         = 65535
    protocol        = "tcp"
    security_groups = [var.alb_sg_id]
  }

  # Allow all outbound traffic so services can reach external APIs via NAT GW
  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-backend-sg"
  })
}
