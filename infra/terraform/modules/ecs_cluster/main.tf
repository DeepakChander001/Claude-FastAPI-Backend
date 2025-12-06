# ============================================================================
# ECS Cluster Module
# ============================================================================

variable "cluster_name" {
  type = string
}

variable "use_fargate" {
  type    = bool
  default = true
}

variable "tags" {
  type = map(string)
}

resource "aws_ecs_cluster" "main" {
  name = var.cluster_name

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = var.tags
}

resource "aws_ecs_cluster_capacity_providers" "main" {
  cluster_name = aws_ecs_cluster.main.name

  capacity_providers = var.use_fargate ? ["FARGATE", "FARGATE_SPOT"] : []

  default_capacity_provider_strategy {
    capacity_provider = var.use_fargate ? "FARGATE" : null
    weight            = 1
    base              = 1
  }
}

# Optional: EC2 Launch Template (if use_fargate = false)
# resource "aws_launch_template" "ecs_ec2" {
#   count         = var.use_fargate ? 0 : 1
#   name_prefix   = "${var.cluster_name}-"
#   image_id      = "REPLACE_ME_AMI_ID"
#   instance_type = "t3.medium"
#   user_data     = base64encode(<<-EOF
#     #!/bin/bash
#     echo ECS_CLUSTER=${var.cluster_name} >> /etc/ecs/ecs.config
#   EOF
#   )
# }

output "cluster_arn" {
  value = aws_ecs_cluster.main.arn
}

output "cluster_name" {
  value = aws_ecs_cluster.main.name
}
