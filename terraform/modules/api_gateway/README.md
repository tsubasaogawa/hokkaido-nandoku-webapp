# API Gateway Module

This module creates an AWS API Gateway HTTP API with Lambda integration.

## Features

- HTTP API (cheaper and simpler than REST API)
- Lambda proxy integration
- Default stage with auto-deploy
- Lambda invoke permissions

## Usage

```hcl
module "api_gateway" {
  source = "./modules/api_gateway"

  api_name             = "my-api"
  lambda_function_name = "my-lambda-function"
  lambda_invoke_arn    = "arn:aws:lambda:region:account:function:my-lambda-function"

  tags = {
    Environment = "production"
  }
}
```

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| `api_name` | Name of the API Gateway HTTP API | `string` | - | yes |
| `lambda_function_name` | Name of the Lambda function to integrate | `string` | - | yes |
| `lambda_invoke_arn` | Invoke ARN of the Lambda function | `string` | - | yes |
| `tags` | Tags to apply to resources | `map(string)` | `{}` | no |

## Outputs

| Name | Description |
|------|-------------|
| `api_id` | ID of the API Gateway HTTP API |
| `api_endpoint` | Endpoint URL of the API |
| `api_execution_arn` | Execution ARN of the API |
| `stage_id` | ID of the default stage |

## Resources Created

- API Gateway HTTP API
- Default stage (`$default`) with auto-deploy enabled
- Lambda integration with proxy configuration
- Default route (`$default`) for all requests
- Lambda permission for API Gateway invocation

## Notes

- Uses HTTP API v2 (not REST API)
- Payload format version 2.0 for Lambda integration
- All routes default to Lambda function
