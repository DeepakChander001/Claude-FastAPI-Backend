# ============================================================================
# Variables for Claude-Proxy Infrastructure
# ============================================================================

variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "REPLACE_ME_REGION"
}

variable "cluster_name" {
  description = "Name of the ECS cluster"
  type        = string
  default     = "claude-proxy"
}

variable "vpc_id" {
  description = "ID of the existing VPC"
  type        = string
  default     = "REPLACE_ME_VPC_ID"
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs for ALB"
  type        = list(string)
  default     = ["REPLACE_ME_SUBNET_1", "REPLACE_ME_SUBNET_2"]
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for ECS tasks"
  type        = list(string)
  default     = ["REPLACE_ME_SUBNET_3", "REPLACE_ME_SUBNET_4"]
}

variable "use_fargate" {
  description = "Use Fargate (true) or EC2 (false) for ECS"
  type        = bool
  default     = true
}

variable "desired_count_api" {
  description = "Desired count of API service tasks"
  type        = number
  default     = 2
}

variable "desired_count_worker" {
  description = "Desired count of Worker service tasks"
  type        = number
  default     = 1
}

variable "tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Project     = "claude-proxy"
    Environment = "staging"
    ManagedBy   = "terraform"
  }
}
