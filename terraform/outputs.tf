# Output values for the deployed infrastructure

output "cloudfront_url" {
  description = "The URL of the CloudFront Distribution"
  value       = module.cloudfront.domain_name
}

output "cloudfront_distribution_id" {
  description = "The ID of the CloudFront Distribution"
  value       = module.cloudfront.distribution_id
}

output "api_gateway_endpoint" {
  description = "The endpoint URL of the API Gateway"
  value       = module.api_gateway.api_endpoint
}

output "lambda_function_name" {
  description = "The name of the Lambda function"
  value       = module.lambda.lambda_function_name
}

output "dynamodb_table_name" {
  description = "The name of the DynamoDB cache table"
  value       = module.dynamodb.table_name
}
