variable "aws_region" {
  description = "The AWS region to deploy resources in."
  type        = string
  default     = "ap-northeast-1"
}

variable "lambda_function_name" {
  description = "The name of the Lambda function."
  type        = string
  default     = "hokkaido-nandoku-quiz"
}

variable "api_endpoint" {
  description = "The endpoint of the backend API."
  type        = string
  sensitive   = true
}
