# ============================================================================
# CloudFront Access Logs to S3 - Example Template
# ============================================================================
# Enables CloudFront access logging to an S3 bucket.
# Replace all REPLACE_ME placeholders before applying.
# ============================================================================

variable "log_bucket_name" {
  description = "S3 bucket for CloudFront logs"
  type        = string
  default     = "REPLACE_ME_LOG_BUCKET"
}

resource "aws_s3_bucket" "logs" {
  bucket = var.log_bucket_name

  tags = {
    Name = "claude-proxy-cf-logs"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id

  rule {
    id     = "expire-old-logs"
    status = "Enabled"

    expiration {
      days = 90
    }

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }
  }
}

resource "aws_s3_bucket_ownership_controls" "logs" {
  bucket = aws_s3_bucket.logs.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

# CloudFront logging configuration
# Add to your cloudfront_distribution resource:
# logging_config {
#   bucket          = aws_s3_bucket.logs.bucket_domain_name
#   prefix          = "cloudfront/"
#   include_cookies = false
# }

# Optional: Kinesis Firehose for real-time log ingestion
# resource "aws_kinesis_firehose_delivery_stream" "cf_logs" {
#   name        = "cloudfront-logs-stream"
#   destination = "extended_s3"
#   # Configure ES/OpenSearch delivery...
# }

output "log_bucket_arn" {
  value = aws_s3_bucket.logs.arn
}
