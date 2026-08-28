# PROVIDER
# Tells Terraform which cloud to connect to

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"   
    }
  }

  required_version = ">= 1.3.0"   
}

provider "aws" {
  region = var.aws_region   
}


# DYNAMODB TABLE
# This is the database where all orders are stored

resource "aws_dynamodb_table" "orders" {
  name         = var.dynamodb_table_name   
  billing_mode = "PAY_PER_REQUEST"         
  
  hash_key = "PK"

  range_key = "SK"

  attribute {
    name = "PK"
    type = "S"   # String
  }

  attribute {
    name = "SK"
    type = "S"   # String (UUID like "ord-550e8400-e29b...")
  }

  tags = {
    Project     = var.project_name
    Environment = "dev"
    ManagedBy   = "Terraform"
  }
}


# IAM ROLE FOR LAMBDA
# Allows Lambda functions to be executed by AWS

resource "aws_iam_role" "lambda_execution_role" {
  name = "${var.project_name}-lambda-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = { Service = "lambda.amazonaws.com" }
        Action    = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Project   = var.project_name
    ManagedBy = "Terraform"
  }
}


# IAM POLICY — CloudWatch Logs
# Allows Lambda to write logs to CloudWatch

resource "aws_iam_role_policy_attachment" "lambda_basic_logs" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}


# IAM POLICY — DynamoDB Access
# Allows Lambda to read/write orders in DynamoDB
# Follows LEAST PRIVILEGE: only the exact actions needed

resource "aws_iam_policy" "lambda_dynamodb_policy" {
  name        = "${var.project_name}-lambda-dynamodb-policy"
  description = "Allows Lambda functions to perform order operations on DynamoDB"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",      
          "dynamodb:GetItem",      
          "dynamodb:UpdateItem",   
          "dynamodb:Query"         
        ]
        Resource = aws_dynamodb_table.orders.arn
      }
    ]
  })
}

# Attach the DynamoDB policy to the Lambda role
resource "aws_iam_role_policy_attachment" "lambda_dynamodb_attach" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.lambda_dynamodb_policy.arn
}


# LAMBDA — Package the Python code into ZIP file

# Zip each Lambda function's folder
data "archive_file" "create_order_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda/create_order"  
  output_path = "${path.module}/zips/create_order.zip"    
}

data "archive_file" "read_order_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda/read_order"
  output_path = "${path.module}/zips/read_order.zip"
}

data "archive_file" "update_status_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda/update_status"
  output_path = "${path.module}/zips/update_status.zip"
}


# CLOUDWATCH LOG GROUPS
# Explicitly create log groups so we control retention
# (Otherwise Lambda creates them automatically with infinite retention = $$$)

resource "aws_cloudwatch_log_group" "create_order_logs" {
  name              = "/aws/lambda/${var.project_name}-create-order"
  retention_in_days = 7   
}

resource "aws_cloudwatch_log_group" "read_order_logs" {
  name              = "/aws/lambda/${var.project_name}-read-order"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_group" "update_status_logs" {
  name              = "/aws/lambda/${var.project_name}-update-status"
  retention_in_days = 7
}


# LAMBDA FUNCTIONS

resource "aws_lambda_function" "create_order" {
  function_name = "${var.project_name}-create-order"
  description   = "Creates a new order (POST /orders)"

  # The zip file Terraform built above
  filename         = data.archive_file.create_order_zip.output_path
  # This hash ensures Terraform re-deploys the Lambda if the code changes
  source_code_hash = data.archive_file.create_order_zip.output_base64sha256

  # "handler.py" file, "lambda_handler" function inside it
  handler = "handler.lambda_handler"
  runtime = var.lambda_runtime   # "python3.12"

  # The IAM role created — gives this function permission to use DynamoDB + CloudWatch
  role = aws_iam_role.lambda_execution_role.arn

  timeout     = 10    # seconds — kill the function if it runs longer than this
  memory_size = 128   # MB

  # Environment variables for the Lambda function
  environment {
    variables = {
      DYNAMODB_TABLE_NAME = var.dynamodb_table_name
    }
  }

  # Ensure the log group is created before the Lambda function
  depends_on = [aws_cloudwatch_log_group.create_order_logs]

  tags = {
    Project   = var.project_name
    ManagedBy = "Terraform"
  }
}

resource "aws_lambda_function" "read_order" {
  function_name    = "${var.project_name}-read-order"
  description      = "Reads one or all orders (GET /orders, GET /orders/{orderId})"
  filename         = data.archive_file.read_order_zip.output_path
  source_code_hash = data.archive_file.read_order_zip.output_base64sha256
  handler          = "handler.lambda_handler"
  runtime          = var.lambda_runtime
  role             = aws_iam_role.lambda_execution_role.arn
  timeout          = 10
  memory_size      = 128

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = var.dynamodb_table_name
    }
  }

  depends_on = [aws_cloudwatch_log_group.read_order_logs]

  tags = {
    Project   = var.project_name
    ManagedBy = "Terraform"
  }
}

resource "aws_lambda_function" "update_status" {
  function_name    = "${var.project_name}-update-status"
  description      = "Updates order status (PATCH /orders/{orderId}/status)"
  filename         = data.archive_file.update_status_zip.output_path
  source_code_hash = data.archive_file.update_status_zip.output_base64sha256
  handler          = "handler.lambda_handler"
  runtime          = var.lambda_runtime
  role             = aws_iam_role.lambda_execution_role.arn
  timeout          = 10
  memory_size      = 128

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = var.dynamodb_table_name
    }
  }

  depends_on = [aws_cloudwatch_log_group.update_status_logs]

  tags = {
    Project   = var.project_name
    ManagedBy = "Terraform"
  }
}