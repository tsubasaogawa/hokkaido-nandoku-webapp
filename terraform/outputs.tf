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

output "acm_certificate_validation_records" {
  description = "DNS validation records for ACM certificate (if custom domain is configured)"
  value = var.domain_name != "" ? [
    for dvo in aws_acm_certificate.cloudfront[0].domain_validation_options : {
      name   = dvo.resource_record_name
      type   = dvo.resource_record_type
      value  = dvo.resource_record_value
      domain = dvo.domain_name
    }
  ] : []
}

output "custom_domain_name" {
  description = "Custom domain name configured for CloudFront (if any)"
  value       = var.domain_name
}
