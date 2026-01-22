# CloudFront Module Variables

variable "origin_domain_name" {
  description = "Domain name of the origin (API Gateway endpoint without https://)"
  type        = string

  validation {
    condition     = !can(regex("^https?://", var.origin_domain_name))
    error_message = "Origin domain name should not include protocol (http:// or https://)."
  }
}

variable "origin_id" {
  description = "Unique identifier for the origin"
  type        = string
  default     = "apigw-origin"
}

variable "comment" {
  description = "Comment for the CloudFront distribution"
  type        = string
  default     = ""
}

variable "custom_header_name" {
  description = "Name of the custom header to add to origin requests"
  type        = string
}

variable "custom_header_value" {
  description = "Value of the custom header to add to origin requests"
  type        = string
  sensitive   = true
}

variable "cache_policy_id" {
  description = "ID of the cache policy to use"
  type        = string
  default     = "4135ea2d-6df8-44a3-9df3-4b5a84be39ad" # Managed-CachingDisabled
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
