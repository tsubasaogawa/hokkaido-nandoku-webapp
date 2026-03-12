# Main Terraform Configuration
# This file orchestrates the deployment of the Hokkaido Nandoku Quiz application

# Generate a random secret for CloudFront -> API Gateway authentication
resource "random_password" "cf_secret" {
  length  = 32
  special = false
}

# ACM Certificate for CloudFront (must be in us-east-1)
resource "aws_acm_certificate" "cloudfront" {
  count = var.domain_name != "" ? 1 : 0

  provider          = aws.us_east_1
  domain_name       = var.domain_name
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = merge(
    local.common_tags,
    {
      Name = "cloudfront-certificate"
    }
  )
}

# DynamoDB Table for quiz caching
module "dynamodb" {
  source = "./modules/dynamodb"

  table_name    = local.dynamodb_table_name
  billing_mode  = "PAY_PER_REQUEST"
  hash_key      = "cache_key"
  ttl_attribute = "expires_at"
  ttl_enabled   = true

  tags = local.common_tags
}

# Lambda Function for quiz application
import {
  to = module.lambda.aws_cloudwatch_log_group.lambda[0]
  id = "/aws/lambda/hokkaido-nandoku-quiz"
}
module "lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 7.0"

  function_name = local.lambda_function_name
  handler       = local.lambda_handler
  runtime       = local.lambda_runtime
  timeout       = local.lambda_timeout

  source_path = "${path.module}/../src"

  # Install Python dependencies during build
  build_in_docker = true

  artifacts_dir = "${path.module}/../.terraform-lambda-builds"

  environment_variables = {
    NANDOKU_API_ENDPOINT = "https://${var.api_endpoint}"
    CF_HEADER_SECRET     = random_password.cf_secret.result
    DYNAMODB_TABLE_NAME  = module.dynamodb.table_name
    BEDROCK_MODEL_ID     = local.bedrock_model_id
  }

  # IAM role configuration
  attach_policy_statements = true
  policy_statements = {
    bedrock_access = {
      effect = "Allow"
      actions = [
        "bedrock:InvokeModel"
      ]
      resources = ["*"]
    }
    marketplace_access = {
      effect = "Allow"
      actions = [
        "aws-marketplace:ViewSubscriptions",
        "aws-marketplace:Subscribe"
      ]
      resources = ["*"]
    }
    dynamodb_access = {
      effect = "Allow"
      actions = [
        "dynamodb:GetItem",
        "dynamodb:PutItem"
      ]
      resources = [module.dynamodb.table_arn]
    }
  }

  tags = local.common_tags
}

# API Gateway HTTP API
module "api_gateway" {
  source = "./modules/api_gateway"

  api_name             = local.api_gateway_name
  lambda_function_name = module.lambda.lambda_function_name
  lambda_invoke_arn    = module.lambda.lambda_function_invoke_arn

  tags = local.common_tags
}

# CloudFront Distribution
module "cloudfront" {
  source = "./modules/cloudfront"

  origin_domain_name = replace(module.api_gateway.api_endpoint, "https://", "")
  origin_id          = "apigw-origin"
  comment            = local.cloudfront_comment

  custom_header_name  = "X-CF-Secret"
  custom_header_value = random_password.cf_secret.result

  # Custom domain configuration
  domain_name     = var.domain_name
  certificate_arn = var.domain_name != "" ? aws_acm_certificate.cloudfront[0].arn : ""

  tags = local.common_tags
}

# --- Step Functions Cache Generation Flow ---

# EventBridge Connection for HTTP Invoke
resource "aws_cloudwatch_event_connection" "nandoku_api" {
  name               = "${local.api_gateway_name}-connection"
  description        = "Connection for Nandoku API HTTP Invoke"
  authorization_type = "API_KEY"

  auth_parameters {
    api_key {
      key   = "x-api-key"
      value = "dummy-value"
    }
  }
}

# IAM Role for Step Functions Execution
resource "aws_iam_role" "sfn_execution_role" {
  name = "${local.api_gateway_name}-sfn-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "states.amazonaws.com"
        }
      }
    ]
  })
}

# Policy allowing HTTP Invoke and Connection credentials retrieval
resource "aws_iam_policy" "sfn_http_invoke_policy" {
  name = "${local.api_gateway_name}-sfn-http-invoke"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "states:InvokeHTTPEndpoint"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "events:RetrieveConnectionCredentials"
        ]
        Resource = aws_cloudwatch_event_connection.nandoku_api.arn
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = aws_cloudwatch_event_connection.nandoku_api.secret_arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "sfn_http_invoke_attach" {
  role       = aws_iam_role.sfn_execution_role.name
  policy_arn = aws_iam_policy.sfn_http_invoke_policy.arn
}

# Step Functions State Machine
resource "aws_sfn_state_machine" "cache_generation_flow" {
  name     = "${local.api_gateway_name}-cache-generation"
  role_arn = aws_iam_role.sfn_execution_role.arn

  definition = jsonencode({
    Comment = "Cache Generation Flow for Hokkaido Nandoku Webapp"
    StartAt = "ListItems"
    States = {
      ListItems = {
        Type     = "Task"
        Resource = "arn:aws:states:::http:invoke"
        Parameters = {
          "ApiEndpoint" = "https://${var.api_endpoint}/v1/list"
          "Method"      = "GET"
          "Authentication" = {
            "ConnectionArn" = aws_cloudwatch_event_connection.nandoku_api.arn
          }
        }
        Next       = "ProcessItems"
        ResultPath = "$.ListResult"
      }
      ProcessItems = {
        Type           = "Map"
        ItemsPath      = "$.ListResult.ResponseBody"
        MaxConcurrency = 5
        ItemProcessor = {
          ProcessorConfig = {
            Mode = "INLINE"
          }
          StartAt = "GenerateCache"
          States = {
            GenerateCache = {
              Type     = "Task"
              Resource = "arn:aws:states:::http:invoke"
              Parameters = {
                "ApiEndpoint.$" = "States.Format('https://${var.api_endpoint}/v1/id/{}', $.id)"
                "Method"        = "GET"
                "Authentication" = {
                  "ConnectionArn" = aws_cloudwatch_event_connection.nandoku_api.arn
                }
              }
              End = true
            }
          }
        }
        End = true
      }
    }
  })

  tags = local.common_tags
}
