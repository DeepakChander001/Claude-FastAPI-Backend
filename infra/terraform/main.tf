# ============================================================================
# Claude-Proxy AWS Infrastructure - Root Module
# ============================================================================
# This module orchestrates all infrastructure for the Claude proxy backend.
# Run with: terraform init && terraform plan -out=plan.tfplan
# ============================================================================

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Provider configuration - see provider.tf.example for guidance
# provider "aws" {
#   region = var.aws_region
# }

# ============================================================================
# Modules
# ============================================================================

module "ecs_cluster" {
  source       = "./modules/ecs_cluster"
  cluster_name = var.cluster_name
  use_fargate  = var.use_fargate
  tags         = var.tags
}

module "alb" {
  source            = "./modules/alb"
  vpc_id            = var.vpc_id
  public_subnet_ids = var.public_subnet_ids
  cluster_name      = var.cluster_name
  tags              = var.tags
}

module "sqs" {
  source       = "./modules/sqs"
  cluster_name = var.cluster_name
  tags         = var.tags
}

module "secrets_manager" {
  source       = "./modules/secrets_manager"
  cluster_name = var.cluster_name
  tags         = var.tags
}

module "iam" {
  source      = "./modules/iam"
  cluster_name = var.cluster_name
  secrets_arn  = module.secrets_manager.secret_arn
  sqs_queue_arn = module.sqs.queue_arn
  tags         = var.tags
}
