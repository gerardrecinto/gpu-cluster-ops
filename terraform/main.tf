terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 6.0" }
  }
}

variable "cluster_name" { type = string }
variable "subnet_ids" { type = list(string) }
variable "node_role_arn" { type = string }
variable "instance_types" {
  type    = list(string)
  default = ["g5.12xlarge"]
}
variable "min_size" {
  type    = number
  default = 0
}
variable "max_size" {
  type    = number
  default = 4
}

# GPU nodes are tainted so only pods that request a GPU land on them.
resource "aws_eks_node_group" "gpu" {
  cluster_name    = var.cluster_name
  node_group_name = "gpu"
  node_role_arn   = var.node_role_arn
  subnet_ids      = var.subnet_ids
  instance_types  = var.instance_types
  ami_type        = "AL2023_x86_64_NVIDIA"
  capacity_type   = "ON_DEMAND"

  scaling_config {
    min_size     = var.min_size
    desired_size = var.min_size
    max_size     = var.max_size
  }

  labels = { "nvidia.com/gpu.present" = "true" }

  taint {
    key    = "nvidia.com/gpu"
    value  = "present"
    effect = "NO_SCHEDULE"
  }

  lifecycle {
    ignore_changes = [scaling_config[0].desired_size] # the autoscaler owns this
  }
}
