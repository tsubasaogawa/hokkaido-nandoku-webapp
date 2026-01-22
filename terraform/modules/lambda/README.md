# Lambda Module

This module creates an AWS Lambda function with associated IAM role and permissions for the Hokkaido Nandoku Quiz application.

## Features

- Lambda function with configurable runtime, handler, and timeout
- IAM role with least privilege permissions
- Bedrock API access for AI-powered quiz generation
- DynamoDB access for caching
- CloudWatch Logs integration
- Automatic deployment package handling

## Usage

```hcl
module "lambda" {
  source = "./modules/lambda"

  function_name = "my-lambda-function"
  handler       = "main.lambda_handler"
  runtime       = "python3.13"
  timeout       = 30

  source_dir  = "../dist"
  output_path = "../main.zip"

  environment_variables = {
    API_ENDPOINT = "https://api.example.com"
    SECRET_KEY   = var.secret_key
  }

  dynamodb_table_arn = "arn:aws:dynamodb:region:account:table/my-table"

  tags = {
    Environment = "production"
  }
}
```

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| `function_name` | Name of the Lambda function | `string` | - | yes |
| `handler` | Lambda function handler | `string` | `"main.lambda_handler"` | no |
| `runtime` | Lambda function runtime | `string` | `"python3.13"` | no |
| `timeout` | Function timeout in seconds (1-900) | `number` | `30` | no |
| `source_dir` | Directory containing Lambda source code | `string` | - | yes |
| `output_path` | Path for the output ZIP file | `string` | - | yes |
| `environment_variables` | Environment variables for Lambda | `map(string)` | `{}` | no |
| `dynamodb_table_arn` | ARN of the DynamoDB table | `string` | - | yes |
| `tags` | Tags to apply to resources | `map(string)` | `{}` | no |

## Outputs

| Name | Description |
|------|-------------|
| `function_name` | Name of the Lambda function |
| `function_arn` | ARN of the Lambda function |
| `invoke_arn` | Invoke ARN of the Lambda function |
| `role_arn` | ARN of the Lambda execution role |

## IAM Permissions

The Lambda function is granted the following permissions:

- **CloudWatch Logs**: Write logs via `AWSLambdaBasicExecutionRole`
- **Bedrock**: Invoke AI models via `bedrock:InvokeModel`
- **AWS Marketplace**: View and subscribe to marketplace products
- **DynamoDB**: Read and write to the specified cache table

## Validation Rules

- Function name: 1-64 characters
- Runtime: Must be a valid Python 3.x version
- Timeout: 1-900 seconds

## Notes

- The module automatically creates a ZIP archive from the source directory
- IAM role follows the principle of least privilege
- CloudWatch Logs are automatically enabled
