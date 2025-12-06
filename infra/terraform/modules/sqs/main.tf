# ============================================================================
# SQS Queue Module
# ============================================================================

variable "cluster_name" {
  type = string
}

variable "tags" {
  type = map(string)
}

resource "aws_sqs_queue" "dlq" {
  name = "${var.cluster_name}-dlq"
  tags = var.tags
}

resource "aws_sqs_queue" "main" {
  name                       = "${var.cluster_name}-jobs"
  visibility_timeout_seconds = 300
  message_retention_seconds  = 1209600 # 14 days
  receive_wait_time_seconds  = 10

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = 3
  })

  tags = var.tags
}

output "queue_url" {
  value = aws_sqs_queue.main.url
}

output "queue_arn" {
  value = aws_sqs_queue.main.arn
}

output "dlq_url" {
  value = aws_sqs_queue.dlq.url
}
