# ===========================================================================
# IAM — Four roles required for ECS on EC2
#
#  Role 1: ecs_instance_role       → EC2 host joins the cluster, SSM, CW logs
#  Role 2: ecs_task_execution_role → ECS pulls ECR image, writes CW logs
#  Role 3: ecs_task_role           → running container calls AWS services
#  Role 4: ecs_service_role        → ECS service manages load-balancer targets
# ===========================================================================

# ---------------------------------------------------------------------------
# ROLE 1: ECS Instance Role
# Assumed by: EC2 instances in the Auto Scaling Group
# Allows: ECS agent to register host, SSM Session Manager access, CW logs
# ---------------------------------------------------------------------------
resource "aws_iam_role" "ecs_instance_role" {
  name = "${var.project_name}-${var.environment}-ecs-instance-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })

  tags = local.common_tags
}

# Registers EC2 instances with the ECS cluster and enables the ECS agent
resource "aws_iam_role_policy_attachment" "ecs_instance_ecs" {
  role       = aws_iam_role.ecs_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

# Allows SSM Session Manager — so engineers can shell into EC2 without SSH keys
resource "aws_iam_role_policy_attachment" "ecs_instance_ssm" {
  role       = aws_iam_role.ecs_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# Allows the CloudWatch agent on the EC2 host to push container logs and metrics
resource "aws_iam_role_policy_attachment" "ecs_instance_cloudwatch" {
  role       = aws_iam_role.ecs_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

# Instance profile wraps the role so it can be attached to an EC2 instance
resource "aws_iam_instance_profile" "ecs_instance_profile" {
  name = "${var.project_name}-${var.environment}-ecs-instance-profile"
  role = aws_iam_role.ecs_instance_role.name
  tags = local.common_tags
}

# ---------------------------------------------------------------------------
# ROLE 2: ECS Task Execution Role
# Assumed by: ECS agent on behalf of the task (NOT the container itself)
# Allows: pull private ECR images, write CloudWatch Logs, read SSM secrets
# ---------------------------------------------------------------------------
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "${var.project_name}-${var.environment}-ecs-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })

  tags = local.common_tags
}

# Grants ECR pull (ecr:GetAuthorizationToken, ecr:BatchGetImage, etc.)
# and CloudWatch Logs write (logs:CreateLogStream, logs:PutLogEvents)
resource "aws_iam_role_policy_attachment" "task_execution_ecs" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Allows ECS to read SSM Parameter Store values during task startup
resource "aws_iam_role_policy_attachment" "task_execution_ssm" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# ---------------------------------------------------------------------------
# ROLE 3: ECS Task Role
# Assumed by: the running application container itself (not the ECS agent)
# Allows: container code to call AWS APIs (S3, DynamoDB, Secrets Manager, etc.)
#
# ⚠️  AdministratorAccess is intentionally used for development/testing only.
#     For PRODUCTION: replace AdministratorAccess with least-privilege policies
#     scoped to the specific AWS services the application requires
#     (e.g. s3:GetObject, secretsmanager:GetSecretValue, etc.).
# ---------------------------------------------------------------------------
resource "aws_iam_role" "ecs_task_role" {
  name = "${var.project_name}-${var.environment}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })

  tags = local.common_tags
}

# DEV ONLY: AdministratorAccess — scope down to least-privilege for production
resource "aws_iam_role_policy_attachment" "ecs_task_role_admin" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

# ---------------------------------------------------------------------------
# ROLE 4: ECS Service Role
# Assumed by: ECS service control plane
# Allows: ECS to register/deregister targets in the ALB target group and
#         manage ENIs for service load-balancing operations
# ---------------------------------------------------------------------------
resource "aws_iam_role" "ecs_service_role" {
  name = "${var.project_name}-${var.environment}-ecs-service-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ecs.amazonaws.com" }
    }]
  })

  tags = local.common_tags
}

# Grants the ECS service permission to register/deregister EC2 instances with
# the load balancer target group and manage service-level networking
resource "aws_iam_role_policy_attachment" "ecs_service_role" {
  role       = aws_iam_role.ecs_service_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceRole"
}
