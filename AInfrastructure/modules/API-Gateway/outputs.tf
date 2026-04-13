output "api_gateway_id" {
  description = "HTTP API ID"
  value       = aws_apigatewayv2_api.this.id
}

output "api_gateway_invoke_url" {
  description = "Full invoke URL including the stage name (e.g. .../uat/)"
  value       = aws_apigatewayv2_stage.this.invoke_url
}

output "api_gateway_default_invoke_url" {
  description = "$default stage invoke URL — no stage prefix required (e.g. .../)"
  value       = aws_apigatewayv2_stage.default.invoke_url
}

output "api_gateway_stage_name" {
  description = "Name of the deployed stage"
  value       = aws_apigatewayv2_stage.this.name
}

output "vpc_link_id" {
  description = "ID of the VPC Link V2"
  value       = aws_apigatewayv2_vpc_link.this.id
}

output "vpc_link_sg_id" {
  description = "Security group ID attached to the VPC Link"
  value       = aws_security_group.vpc_link_sg.id
}

output "backend_sg_id" {
  description = "Security group ID for backend compute resources (ECS/EC2)"
  value       = aws_security_group.backend_sg.id
}

output "api_gateway_proxy_route_id" {
  description = "Route ID for ANY /{proxy+}"
  value       = aws_apigatewayv2_route.proxy.id
}

output "api_gateway_root_route_id" {
  description = "Route ID for ANY /"
  value       = aws_apigatewayv2_route.root.id
}
