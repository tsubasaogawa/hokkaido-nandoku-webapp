# Lambda Module Variables

variable "function_name" {
  description = "Name of the Lambda function"
  type        = string

  validation {
    condition     = length(var.function_name) > 0 && length(var.function_name) <= 64
    error_message = "Function name must be between 1 and 64 characters."
  }
}

variable "handler" {
  description = "Lambda function handler"
  type        = string
  default     = "main.lambda_handler"
}

variable "runtime" {
  description = "Lambda function runtime"
  type        = string
  default     = "python3.13"

  validation {
    condition     = can(regex("^python3\\.(\\d+)$", var.runtime))
    error_message = "Runtime must be a valid Python 3.x version."
  }
}

variable "timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 30

  validation {
    condition     = var.timeout >= 1 && var.timeout <= 900
    error_message = "Timeout must be between 1 and 900 seconds."
  }
}

variable "source_dir" {
  description = "Directory containing Lambda source code"
  type        = string
}

variable "output_path" {
  description = "Path for the output ZIP file"
  type        = string
}

variable "environment_variables" {
  description = "Environment variables for Lambda function"
  type        = map(string)
  default     = {}
}

variable "dynamodb_table_arn" {
  description = "ARN of the DynamoDB table for caching"
  type        = string
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
