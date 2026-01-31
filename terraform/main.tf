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
