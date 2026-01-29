variable "aws_region" {
  description = "The AWS region to create resources in."
  type        = string
  default     = "us-east-1"
}

variable "db_username" {
  description = "The username for the RDS database."
  type        = string
  default     = "postgres"
}

variable "db_password" {
  description = "The password for the RDS database."
  type        = string
  sensitive   = true
  # In a real-world scenario, you should use a more secure way to manage secrets,
  # like AWS Secrets Manager, and not use default passwords.
  # For this free-tier example, we'll use a placeholder.
  # You will be prompted to enter a password on `terraform apply`.
  # Or you can set it via an environment variable TF_VAR_db_password
}


variable "ecr_consumer_image" {
  description = "ECR image URI for consumer"
  type        = string
}

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "main-cluster"
}

variable "ssh_key_name" {
  description = "SSH key name (optional) for remote access to nodes"
  type        = string
  default     = "launchpad-key"
}
