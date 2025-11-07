output "lambda_function_url" {
  description = "The URL of the Lambda Function URL."
  value       = aws_lambda_function_url.this.function_url
}
