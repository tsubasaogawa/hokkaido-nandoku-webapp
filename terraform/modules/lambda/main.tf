# Lambda Function Module
# This module creates the Lambda function, IAM role, and related resources

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = var.source_dir
  output_path = var.output_path
}

resource "aws_iam_role" "lambda_exec" {
  name = "${var.function_name}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })

  inline_policy {
    name = "bedrock-access"
    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Action   = "bedrock:InvokeModel"
          Effect   = "Allow"
          Resource = "*"
        },
        {
          Action = [
            "aws-marketplace:ViewSubscriptions",
            "aws-marketplace:Subscribe"
          ]
          Effect   = "Allow"
          Resource = "*"
        },
        {
          Action = [
            "dynamodb:GetItem",
            "dynamodb:PutItem"
          ]
          Effect   = "Allow"
          Resource = var.dynamodb_table_arn
        }
      ]
    })
  }

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "this" {
  function_name = var.function_name
  role          = aws_iam_role.lambda_exec.arn

  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  handler = var.handler
  runtime = var.runtime
  timeout = var.timeout

  environment {
    variables = var.environment_variables
  }

  tags = var.tags
}
