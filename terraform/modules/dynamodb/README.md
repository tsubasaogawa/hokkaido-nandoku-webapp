# DynamoDB Module

This module creates an AWS DynamoDB table for caching quiz data.

## Features

- On-demand (pay-per-request) billing mode
- TTL (Time To Live) support for automatic data expiration
- Configurable hash key
- Consistent tagging

## Usage

```hcl
module "dynamodb" {
  source = "./modules/dynamodb"

  table_name    = "my-cache-table"
  billing_mode  = "PAY_PER_REQUEST"
  hash_key      = "cache_key"
  ttl_attribute = "expires_at"
  ttl_enabled   = true

  tags = {
    Environment = "production"
  }
}
```

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| `table_name` | Name of the DynamoDB table (3-255 chars) | `string` | - | yes |
| `billing_mode` | Billing mode (PROVISIONED or PAY_PER_REQUEST) | `string` | `"PAY_PER_REQUEST"` | no |
| `hash_key` | Hash key attribute name | `string` | `"cache_key"` | no |
| `ttl_attribute` | TTL attribute name | `string` | `"expires_at"` | no |
| `ttl_enabled` | Whether TTL is enabled | `bool` | `true` | no |
| `tags` | Tags to apply to resources | `map(string)` | `{}` | no |

## Outputs

| Name | Description |
|------|-------------|
| `table_name` | Name of the DynamoDB table |
| `table_arn` | ARN of the DynamoDB table |
| `table_id` | ID of the DynamoDB table |

## Table Schema

The table is created with:
- **Hash Key**: String attribute (configurable name)
- **Billing Mode**: On-demand (pay per request)
- **TTL**: Enabled on configurable attribute

## Cost Optimization

- Uses `PAY_PER_REQUEST` billing mode to only pay for actual usage
- TTL automatically removes expired items to reduce storage costs
- No provisioned capacity means no idle capacity charges

## Validation Rules

- Table name: 3-255 characters
- Billing mode: Must be either `PROVISIONED` or `PAY_PER_REQUEST`

## Notes

- TTL expiration happens within 48 hours of the specified time
- Hash key attribute type is String (S)
- Table is encrypted at rest using AWS managed keys by default
