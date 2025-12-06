# ------------------------------------------------------------------------
# ECS Service & Task Definition (Snippet)
# ------------------------------------------------------------------------
# This is a reference snippet for creating the ECS Service and Task Definition.
# It assumes VPC, Subnets, Security Groups, and ALB are already defined.

# resource "aws_ecs_task_definition" "app" {
#   family                   = "claude-proxy-task"
#   network_mode             = "awsvpc"
#   requires_compatibilities = ["FARGATE"]
#   cpu                      = 512  # 0.5 vCPU
#   memory                   = 1024 # 1 GB
#   execution_role_arn       = aws_iam_role.ecs_execution_role.arn
#   task_role_arn            = aws_iam_role.ecs_task_role.arn
#
#   container_definitions = jsonencode([
#     {
#       name      = "claude-proxy-app"
#       image     = var.container_image # e.g., 123456789012.dkr.ecr.us-east-1.amazonaws.com/repo:tag
#       essential = true
#       portMappings = [
#         {
#           containerPort = 8000
#           hostPort      = 8000
#           protocol      = "tcp"
#         }
#       ]
#       environment = [
#         { name = "ENVIRONMENT", value = "production" },
#         { name = "AWS_SECRETS_MANAGER_ENABLED", value = "true" },
#         { name = "AWS_SECRETS_NAME", value = var.secrets_name }
#       ]
#       # Secrets injected as env vars from Secrets Manager
#       secrets = [
#         {
#           name      = "ANTHROPIC_API_KEY"
#           valueFrom = "${var.secrets_arn}:ANTHROPIC_API_KEY::"
#         }
#       ]
#       logConfiguration = {
#         logDriver = "awslogs"
#         options = {
#           "awslogs-group"         = "/ecs/claude-proxy"
#           "awslogs-region"        = var.aws_region
#           "awslogs-stream-prefix" = "ecs"
#         }
#       }
#     }
#   ])
# }

# resource "aws_ecs_service" "app" {
#   name            = "claude-proxy-service"
#   cluster         = aws_ecs_cluster.main.id
#   task_definition = aws_ecs_task_definition.app.arn
#   desired_count   = 2
#   launch_type     = "FARGATE"
#
#   network_configuration {
#     subnets          = var.private_subnets
#     security_groups  = [aws_security_group.ecs_tasks.id]
#     assign_public_ip = false
#   }
#
#   load_balancer {
#     target_group_arn = aws_lb_target_group.app.arn
#     container_name   = "claude-proxy-app"
#     container_port   = 8000
#   }
#
#   # Ignore changes to desired_count if autoscaling is enabled
#   lifecycle {
#     ignore_changes = [desired_count]
#   }
# }

# ------------------------------------------------------------------------
# Autoscaling (Optional)
# ------------------------------------------------------------------------
# resource "aws_appautoscaling_target" "ecs_target" {
#   max_capacity       = 10
#   min_capacity       = 2
#   resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.app.name}"
#   scalable_dimension = "ecs:service:DesiredCount"
#   service_namespace  = "ecs"
# }

# Scale on CPU Utilization
# resource "aws_appautoscaling_policy" "ecs_policy_cpu" {
#   name               = "cpu-autoscaling"
#   policy_type        = "TargetTrackingScaling"
#   resource_id        = aws_appautoscaling_target.ecs_target.resource_id
#   scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
#   service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace
#
#   target_tracking_scaling_policy_configuration {
#     predefined_metric_specification {
#       predefined_metric_type = "ECSServiceAverageCPUUtilization"
#     }
#     target_value = 70.0
#   }
# }
