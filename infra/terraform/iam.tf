# IAM Role for ECS Task Execution
# This role allows ECS agent to pull images and fetch secrets
resource "aws_iam_role" "ecs_execution_role" {
  name = "${var.service_name}-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

# Attach basic execution policy (logs, ECR pull)
resource "aws_iam_role_policy_attachment" "ecs_execution_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Inline policy for Secrets Manager access
resource "aws_iam_role_policy" "secrets_access" {
  name = "SecretsManagerAccess"
  role = aws_iam_role.ecs_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          "arn:aws:secretsmanager:${var.aws_region}:*:secret:${var.secrets_manager_name}-*"
        ]
      }
    ]
  })
}

# IAM Role for the Task itself (if the app needs to call AWS services directly)
resource "aws_iam_role" "ecs_task_role" {
  name = "${var.service_name}-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

# Example: If app needs to call Bedrock or S3, attach policies here
# resource "aws_iam_role_policy_attachment" "task_s3_access" { ... }
