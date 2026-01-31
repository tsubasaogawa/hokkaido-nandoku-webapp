# Input variables for the Terraform configuration

variable "aws_region" {
  description = "The AWS region to deploy resources in"
  type        = string
  default     = "ap-northeast-1"

  validation {
    condition     = can(regex("^[a-z]{2}-[a-z]+-[0-9]+$", var.aws_region))
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
    condition     = can(regex("^[a-zA-Z0-9.-]+\\.(execute-api|amazonaws\\.com|cloudfront\\.net)", var.api_endpoint))
    error_message = "API endpoint must be a valid AWS API Gateway, CloudFront, or AWS service endpoint."
  }
}

variable "cloudfront_domain_name" {
  description = "Custom domain name for CloudFront (e.g., example.com). Leave empty to use default CloudFront domain."
  type        = string
  default     = ""

  validation {
    condition     = var.cloudfront_domain_name == "" || can(regex("^[a-zA-Z0-9][a-zA-Z0-9.-]*[a-zA-Z0-9]$", var.cloudfront_domain_name))
    error_message = "Domain name must be a valid domain format."
  }
}

variable "acm_certificate_domain" {
  description = "Domain name for ACM certificate (e.g., example.com or *.example.com). Required if cloudfront_domain_name is set."
  type        = string
  default     = ""

  validation {
    condition     = var.acm_certificate_domain == "" || can(regex("^(\\*\\.)?[a-zA-Z0-9][a-zA-Z0-9.-]*[a-zA-Z0-9]$", var.acm_certificate_domain))
    error_message = "ACM certificate domain must be a valid domain or wildcard domain format."
  }
}
