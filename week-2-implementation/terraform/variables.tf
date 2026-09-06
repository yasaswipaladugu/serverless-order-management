variable "aws_region" {
  description = "The AWS region where all resources will be created"
  type        = string
  default     = "eu-central-1"
}

variable "project_name" {
  description = "A short name used to prefix all resources so they are easy to find in AWS"
  type        = string
  default     = "orderflow"
}

variable "dynamodb_table_name" {
  description = "The name of the DynamoDB table that stores orders"
  type        = string
  default     = "orders"
}

variable "lambda_runtime" {
  description = "The Python runtime version for all Lambda functions"
  type        = string
  default     = "python3.12"
}
