# API Gateway Module Outputs

output "api_id" {
  description = "ID of the API Gateway HTTP API"
  value       = aws_apigatewayv2_api.http_api.id
}

output "api_endpoint" {
  description = "Endpoint URL of the API Gateway HTTP API"
  value       = aws_apigatewayv2_api.http_api.api_endpoint
}

output "api_execution_arn" {
  description = "Execution ARN of the API Gateway HTTP API"
  value       = aws_apigatewayv2_api.http_api.execution_arn
}

output "stage_id" {
  description = "ID of the default stage"
  value       = aws_apigatewayv2_stage.default.id
}
