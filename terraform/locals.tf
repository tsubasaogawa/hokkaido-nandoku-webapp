# Local values for reusability and consistency

locals {
  # Project information
  project_name = "hokkaido-nandoku-quiz"
  environment  = "production"

  # Common tags applied to all resources
  common_tags = {
    Project     = "Hokkaido Nandoku Quiz"
    ManagedBy   = "Terraform"
    Environment = local.environment
    Repository  = "tsubasaogawa/hokkaido-nandoku-webapp"
  }

  # Lambda configuration
  lambda_function_name = var.lambda_function_name
  lambda_handler       = "main.lambda_handler"
  lambda_runtime       = "python3.13"
  lambda_timeout       = 30

  # DynamoDB configuration
  dynamodb_table_name = "${local.project_name}-cache"

  # API Gateway configuration
  api_gateway_name = local.project_name

  # CloudFront configuration
  cloudfront_comment = "Hokkaido Nandoku Quiz CloudFront Distribution"
}
