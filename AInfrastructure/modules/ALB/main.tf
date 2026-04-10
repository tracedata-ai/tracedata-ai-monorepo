# ---------------------------------------------------------------------------
# locals — shared tags applied to every resource to avoid repetition
# ---------------------------------------------------------------------------
locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# ---------------------------------------------------------------------------
# Security Group — restricts ALB traffic to the VPC CIDR only.
# Inbound:  HTTP (80) from var.vpc_cidr.
# Outbound: all protocols to var.vpc_cidr (no internet egress).
# ---------------------------------------------------------------------------
resource "aws_security_group" "alb_sg" {
  name        = "${var.project_name}-${var.environment}-alb-sg"
  description = "Internal ALB SG - allow HTTP from VPC CIDR only"
  vpc_id      = var.vpc_id

  # Allow inbound HTTP from within the VPC only — port 443 is NOT needed
  # because TLS is terminated at the API Gateway layer upstream of this ALB.
  ingress {
    description = "HTTP from VPC CIDR"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  # Restrict outbound to VPC CIDR only — no 0.0.0.0/0 egress
  egress {
    description = "All traffic to VPC CIDR"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [var.vpc_cidr]
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-alb-sg"
  })
}

# ---------------------------------------------------------------------------
# Internal Application Load Balancer — deployed across both private subnets.
# internal = true means it is NOT internet-facing.
# ---------------------------------------------------------------------------
resource "aws_lb" "internal" {
  name               = var.alb_name
  internal           = true
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = var.private_subnet_ids

  enable_deletion_protection = var.enable_deletion_protection

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-alb"
  })
}

# ---------------------------------------------------------------------------
# Target Group — backend services receive HTTP traffic on port 80.
# target_type is a variable: "ip" for ECS/Fargate, "instance" for EC2.
# ---------------------------------------------------------------------------
resource "aws_lb_target_group" "app" {
  name                 = var.target_group_name
  port                 = 80
  protocol             = "HTTP"
  vpc_id               = var.vpc_id
  target_type          = var.target_type
  deregistration_delay = var.deregistration_delay

  health_check {
    path                = var.health_check_path
    protocol            = "HTTP"
    port                = "traffic-port" # uses the dynamic port ECS registers on the host
    healthy_threshold   = 3
    unhealthy_threshold = 3
    interval            = 30
    timeout             = 5
    matcher             = "200-399" # Next.js may return 200, 304 etc.
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-tg"
  })
}

# ---------------------------------------------------------------------------
# HTTP Listener (port 80) — forwards all traffic directly to the target group.
# TLS is terminated at the API Gateway layer, so no HTTPS listener is needed
# and no redirect action is added here.
# ---------------------------------------------------------------------------
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.internal.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}
