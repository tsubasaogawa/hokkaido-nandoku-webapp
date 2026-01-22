# DynamoDB Module Variables

variable "table_name" {
  description = "Name of the DynamoDB table"
  type        = string

  validation {
    condition     = length(var.table_name) >= 3 && length(var.table_name) <= 255
    error_message = "Table name must be between 3 and 255 characters."
  }
}

variable "billing_mode" {
  description = "Billing mode for the DynamoDB table"
  type        = string
  default     = "PAY_PER_REQUEST"

  validation {
    condition     = contains(["PROVISIONED", "PAY_PER_REQUEST"], var.billing_mode)
    error_message = "Billing mode must be either PROVISIONED or PAY_PER_REQUEST."
  }
}

variable "hash_key" {
  description = "Hash key attribute name"
  type        = string
  default     = "cache_key"
}

variable "ttl_attribute" {
  description = "TTL attribute name"
  type        = string
  default     = "expires_at"
}

variable "ttl_enabled" {
  description = "Whether TTL is enabled"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
