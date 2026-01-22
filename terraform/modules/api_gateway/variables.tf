# API Gateway Module Variables

variable "api_name" {
  description = "Name of the API Gateway HTTP API"
  type        = string

  validation {
    condition     = length(var.api_name) > 0
    error_message = "API name must not be empty."
  }
}

variable "lambda_function_name" {
  description = "Name of the Lambda function to integrate with"
  type        = string
}

variable "lambda_invoke_arn" {
  description = "Invoke ARN of the Lambda function"
  type        = string
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
