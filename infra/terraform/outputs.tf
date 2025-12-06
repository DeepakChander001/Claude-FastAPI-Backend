# ============================================================================
# Outputs
# ============================================================================

output "alb_dns" {
  description = "DNS name of the Application Load Balancer"
  value       = module.alb.alb_dns
}

output "ecs_cluster_arn" {
  description = "ARN of the ECS cluster"
  value       = module.ecs_cluster.cluster_arn
}

output "sqs_queue_url" {
  description = "URL of the SQS job queue"
  value       = module.sqs.queue_url
}

output "secrets_arn" {
  description = "ARN of the Secrets Manager secret"
  value       = module.secrets_manager.secret_arn
  sensitive   = true
}

output "task_execution_role_arn" {
  description = "ARN of the ECS task execution role"
  value       = module.iam.task_execution_role_arn
}

output "task_role_arn" {
  description = "ARN of the ECS task role"
  value       = module.iam.task_role_arn
}
