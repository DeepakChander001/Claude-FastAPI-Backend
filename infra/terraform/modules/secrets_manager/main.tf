# ============================================================================
# Secrets Manager Module
# ============================================================================

variable "cluster_name" {
  type = string
}

variable "tags" {
  type = map(string)
}

resource "aws_secretsmanager_secret" "app_secrets" {
  name = "${var.cluster_name}-secrets"
  tags = var.tags
}

resource "aws_secretsmanager_secret_version" "app_secrets" {
  secret_id = aws_secretsmanager_secret.app_secrets.id
  secret_string = jsonencode({
    ANTHROPIC_API_KEY  = "REPLACE_ME"
    SUPABASE_KEY       = "REPLACE_ME"
    SUPABASE_URL       = "REPLACE_ME"
    JWT_SECRET         = "REPLACE_ME"
    ALLOWED_API_KEYS   = "REPLACE_ME,REPLACE_ME"
  })
}

# To update secret values post-creation:
# aws secretsmanager put-secret-value \
#   --secret-id claude-proxy-secrets \
#   --secret-string '{"ANTHROPIC_API_KEY":"real-key","...":"..."}'

output "secret_arn" {
  value = aws_secretsmanager_secret.app_secrets.arn
}

output "secret_name" {
  value = aws_secretsmanager_secret.app_secrets.name
}
