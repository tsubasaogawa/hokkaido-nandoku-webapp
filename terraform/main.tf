# Main Terraform Configuration
# This file orchestrates the deployment of the Hokkaido Nandoku Quiz application

# Generate a random secret for CloudFront -> API Gateway authentication
resource "random_password" "cf_secret" {
  length  = 32
  special = false
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
module "lambda" {
  source = "./modules/lambda"

  function_name = local.lambda_function_name
  handler       = local.lambda_handler
  runtime       = local.lambda_runtime
  timeout       = local.lambda_timeout

  source_dir  = "${path.module}/../dist"
  output_path = "${path.module}/../main.zip"

  environment_variables = {
    NANDOKU_API_ENDPOINT = "https://${var.api_endpoint}"
    CF_HEADER_SECRET     = random_password.cf_secret.result
  }

  dynamodb_table_arn = module.dynamodb.table_arn

  tags = local.common_tags
}

# API Gateway HTTP API
module "api_gateway" {
  source = "./modules/api_gateway"

  api_name             = local.api_gateway_name
  lambda_function_name = module.lambda.function_name
  lambda_invoke_arn    = module.lambda.invoke_arn

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

  tags = local.common_tags
}
