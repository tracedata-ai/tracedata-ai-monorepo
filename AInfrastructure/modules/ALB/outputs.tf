output "alb_arn" {
  description = "Full ARN of the internal Application Load Balancer"
  value       = aws_lb.internal.arn
}

output "alb_dns_name" {
  description = "DNS name of the ALB (used by VPC Link or Route 53 records)"
  value       = aws_lb.internal.dns_name
}

output "alb_zone_id" {
  description = "Canonical hosted zone ID of the ALB (for Route 53 alias records)"
  value       = aws_lb.internal.zone_id
}

output "alb_sg_id" {
  description = "Security group ID attached to the internal ALB"
  value       = aws_security_group.alb_sg.id
}

output "target_group_arn" {
  description = "ARN of the target group the HTTP listener forwards traffic to"
  value       = aws_lb_target_group.app.arn
}

output "http_listener_arn" {
  description = "ARN of the HTTP (port 80) listener on the ALB"
  value       = aws_lb_listener.http.arn
}
