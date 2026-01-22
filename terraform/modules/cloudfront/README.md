# CloudFront Module

This module creates an AWS CloudFront distribution for content delivery and edge caching.

## Features

- Global content delivery network (CDN)
- HTTPS redirect for security
- Custom origin header for authentication
- IPv6 support
- Configurable cache policy

## Usage

```hcl
module "cloudfront" {
  source = "./modules/cloudfront"

  origin_domain_name = "api.execute-api.region.amazonaws.com"
  origin_id          = "my-origin"
  comment            = "My CloudFront Distribution"

  custom_header_name  = "X-Custom-Header"
  custom_header_value = var.secret_value

  tags = {
    Environment = "production"
  }
}
```

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| `origin_domain_name` | Domain name of the origin (without https://) | `string` | - | yes |
| `origin_id` | Unique identifier for the origin | `string` | `"apigw-origin"` | no |
| `comment` | Comment for the distribution | `string` | `""` | no |
| `custom_header_name` | Name of custom header for origin requests | `string` | - | yes |
| `custom_header_value` | Value of custom header (sensitive) | `string` | - | yes |
| `cache_policy_id` | ID of the cache policy | `string` | `"4135ea2d-6df8-44a3-9df3-4b5a84be39ad"` | no |
| `tags` | Tags to apply to resources | `map(string)` | `{}` | no |

## Outputs

| Name | Description |
|------|-------------|
| `distribution_id` | ID of the CloudFront distribution |
| `distribution_arn` | ARN of the CloudFront distribution |
| `domain_name` | Domain name of the distribution |
| `hosted_zone_id` | Route 53 zone ID for CloudFront |

## Default Configuration

- **Protocol**: HTTPS only (redirects HTTP to HTTPS)
- **Cache Policy**: Managed-CachingDisabled (`4135ea2d-6df8-44a3-9df3-4b5a84be39ad`)
- **Origin Protocol**: HTTPS only with TLS 1.2
- **Geographic Restrictions**: None
- **IPv6**: Enabled

## Security Features

- HTTPS redirect enforced
- Custom header authentication to origin
- TLS 1.2 minimum
- Default CloudFront certificate

## Notes

- Uses AWS managed cache policy for consistency
- `web_acl_id` changes are ignored (for WAF integration)
- Custom headers are useful for origin authentication
