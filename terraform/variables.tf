# Input variables for the Terraform configuration

variable "aws_region" {
  description = "The AWS region to deploy resources in"
  type        = string
  default     = "ap-northeast-1"

  validation {
    condition     = can(regex("^[a-z]{2}-[a-z]+-[0-9]{1}$", var.aws_region))
    error_message = "AWS region must be in the format: xx-xxxx-x (e.g., ap-northeast-1)."
  }
}

variable "lambda_function_name" {
  description = "The name of the Lambda function"
  type        = string
  default     = "hokkaido-nandoku-quiz"

  validation {
    condition     = length(var.lambda_function_name) > 0 && length(var.lambda_function_name) <= 64
    error_message = "Lambda function name must be between 1 and 64 characters."
  }
}

variable "api_endpoint" {
  description = "The endpoint of the backend API (without https:// and without path)"
  type        = string
  sensitive   = true

  validation {
    condition     = can(regex("^[a-z0-9.-]+\\.(execute-api|amazonaws\\.com)", var.api_endpoint))
    error_message = "API endpoint must be a valid AWS API Gateway or AWS service endpoint."
  }
}
