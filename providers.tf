terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }


  backend "s3" {
    bucket = "heet-s3-bucket"     # set in terraform.tfvars
    key    = "infrastructure/terraform.tfstate"
    region = "us-east-1"
    encrypt = true
    dynamodb_table = "launchpad-table"
  }
}
provider "aws" {
  region = var.aws_region
}
