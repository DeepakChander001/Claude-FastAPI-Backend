# ============================================================================
# PagerDuty Integration Example
# ============================================================================
# This shows how to configure SNS -> PagerDuty integration.
# Required IAM: sns:Subscribe, sns:Publish
# NEVER commit real PagerDuty keys!
# ============================================================================

variable "pagerduty_integration_key" {
  description = "PagerDuty Events API v2 integration key"
  default     = "REPLACE_ME_PAGERDUTY_KEY"
  sensitive   = true
}

# SNS Topic for Alerts
resource "aws_sns_topic" "alerts" {
  name = "claude-proxy-alerts"
}

# SNS Subscription to PagerDuty
# PagerDuty provides an HTTPS endpoint for SNS subscriptions
resource "aws_sns_topic_subscription" "pagerduty" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "https"
  endpoint  = "https://events.pagerduty.com/integration/REPLACE_ME_PAGERDUTY_KEY/enqueue"
}

# Alternative: Lambda to bridge SNS -> PagerDuty
# resource "aws_lambda_function" "pagerduty_bridge" {
#   function_name = "pagerduty-bridge"
#   runtime       = "python3.9"
#   handler       = "index.handler"
#   environment {
#     variables = {
#       PAGERDUTY_KEY = var.pagerduty_integration_key
#     }
#   }
# }

# IAM for Lambda (if using bridge)
# resource "aws_iam_role" "pagerduty_lambda" {
#   name = "pagerduty-lambda-role"
#   assume_role_policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [{
#       Action = "sts:AssumeRole"
#       Effect = "Allow"
#       Principal = { Service = "lambda.amazonaws.com" }
#     }]
#   })
# }

output "alerts_topic_arn" {
  value = aws_sns_topic.alerts.arn
}
