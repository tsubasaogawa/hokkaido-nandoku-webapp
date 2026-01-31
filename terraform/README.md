# Terraform Infrastructure for Hokkaido Nandoku Quiz

This Terraform configuration deploys the infrastructure for the Hokkaido Nandoku Quiz web application on AWS.

## Architecture

The infrastructure consists of the following components:

- **Lambda Function**: Hosts the Python-based web application
- **API Gateway (HTTP API)**: Provides HTTP endpoint for the Lambda function
- **CloudFront Distribution**: CDN and edge caching for the application
- **DynamoDB Table**: Caches quiz data to reduce API calls
- **IAM Roles & Policies**: Secure access control for Lambda execution

## Module Structure

The configuration is organized into reusable modules:

- `modules/lambda`: Lambda function and IAM role configuration
- `modules/api_gateway`: API Gateway HTTP API setup
- `modules/cloudfront`: CloudFront distribution configuration
- `modules/dynamodb`: DynamoDB table for caching

## Prerequisites

- Terraform >= 1.0
- AWS CLI configured with appropriate credentials
- Python 3.13+ (for building the deployment package)
- Backend API endpoint from [hokkaido-nandoku-api](https://github.com/tsubasaogawa/hokkaido-nandoku-api)

## Usage

### 1. Build the Deployment Package

Before running Terraform, you need to create the Lambda deployment package:

```bash
cd ..
mkdir -p dist
rm -rf dist/*
pip install . jinja2 python-multipart -t dist --platform manylinux2014_x86_64 --python-version 3.13 --only-binary=:all:
cp -r src/* dist/
cp -r templates dist/
cd terraform
```

### 2. Initialize Terraform

```bash
terraform init
```

### 3. Plan the Deployment

Review the planned changes:

```bash
terraform plan -var "api_endpoint=YOUR_API_ENDPOINT"
```

**Note**: The `api_endpoint` should be the domain name only (e.g., `ecif1srlak.execute-api.ap-northeast-1.amazonaws.com`), without `https://` and without any path like `/random`.

### 4. Apply the Configuration

Deploy the infrastructure:

```bash
terraform apply -var "api_endpoint=YOUR_API_ENDPOINT"
```

Or use auto-approve for CI/CD:

```bash
terraform apply -var "api_endpoint=YOUR_API_ENDPOINT" -auto-approve
```

### 5. Access the Application

After deployment, Terraform will output the CloudFront URL:

```
cloudfront_url = "d1234567890abc.cloudfront.net"
```

Access the application at: `https://d1234567890abc.cloudfront.net`

## Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `aws_region` | AWS region to deploy resources | `ap-northeast-1` | No |
| `lambda_function_name` | Name of the Lambda function | `hokkaido-nandoku-quiz` | No |
| `api_endpoint` | Backend API endpoint (domain only) | - | Yes |
| `domain_name` | Custom domain name for CloudFront and ACM certificate (supports wildcards) | `""` (empty) | No |

### Custom Domain Configuration

To use a custom domain name instead of the default CloudFront domain:

1. Specify the `domain_name` variable:

```bash
terraform apply \
  -var "api_endpoint=YOUR_API_ENDPOINT" \
  -var "domain_name=example.com"
```

For a wildcard certificate that can be used with any subdomain:
```bash
terraform apply \
  -var "api_endpoint=YOUR_API_ENDPOINT" \
  -var "domain_name=*.example.com"
```

2. After applying, Terraform will output DNS validation records:

```
acm_certificate_validation_records = [
  {
    "domain" = "example.com"
    "name"   = "_xxx.example.com"
    "type"   = "CNAME"
    "value"  = "_yyy.acm-validations.aws."
  }
]
```

3. Add these DNS records to your domain's DNS configuration to validate the certificate.

4. Once validated, add a CNAME or ALIAS record pointing your domain to the CloudFront distribution:
   - Type: CNAME (or ALIAS for Route53)
   - Name: Your domain (e.g., `www.example.com` or `example.com`)
   - Value: CloudFront domain name (from `cloudfront_url` output)

**Note**: The ACM certificate is automatically created in us-east-1 region as required by CloudFront.

## Outputs

| Output | Description |
|--------|-------------|
| `cloudfront_url` | CloudFront distribution domain name |
| `cloudfront_distribution_id` | CloudFront distribution ID |
| `api_gateway_endpoint` | API Gateway endpoint URL |
| `lambda_function_name` | Lambda function name |
| `dynamodb_table_name` | DynamoDB cache table name |
| `acm_certificate_validation_records` | DNS validation records for ACM certificate (if custom domain is configured) |
| `custom_domain_name` | Custom domain name configured for CloudFront (if any) |

## Remote State Backend (Recommended for Production)

For production use, configure a remote backend in `versions.tf`:

1. Create an S3 bucket for state storage:
   ```bash
   aws s3api create-bucket --bucket your-terraform-state-bucket --region ap-northeast-1 --create-bucket-configuration LocationConstraint=ap-northeast-1
   aws s3api put-bucket-versioning --bucket your-terraform-state-bucket --versioning-configuration Status=Enabled
   ```

2. Create a DynamoDB table for state locking:
   ```bash
   aws dynamodb create-table --table-name terraform-state-lock --attribute-definitions AttributeName=LockID,AttributeType=S --key-schema AttributeName=LockID,KeyType=HASH --billing-mode PAY_PER_REQUEST
   ```

3. Uncomment and configure the backend block in `versions.tf`:
   ```hcl
   backend "s3" {
     bucket         = "your-terraform-state-bucket"
     key            = "hokkaido-nandoku-webapp/terraform.tfstate"
     region         = "ap-northeast-1"
     encrypt        = true
     dynamodb_table = "terraform-state-lock"
   }
   ```

4. Re-initialize Terraform:
   ```bash
   terraform init -migrate-state
   ```

## Security Features

- **IAM Least Privilege**: Lambda role has minimal required permissions
- **Encryption**: CloudFront uses HTTPS by default
- **Secret Management**: CloudFront to API Gateway authentication via custom header
- **DynamoDB Encryption**: Table encrypted at rest (AWS managed keys)

## Cost Optimization

- **DynamoDB**: Uses PAY_PER_REQUEST billing mode for cost efficiency
- **Lambda**: Configured with appropriate timeout to prevent overcharges
- **CloudFront**: Uses managed cache policy to reduce origin requests
- **API Gateway**: HTTP API (cheaper than REST API)

## Maintenance

### Updating the Application

1. Update the code in the `src` directory
2. Rebuild the deployment package (see step 1 above)
3. Run `terraform apply`

### Destroying the Infrastructure

To remove all resources:

```bash
terraform destroy -var "api_endpoint=YOUR_API_ENDPOINT"
```

## Module Documentation

Each module has its own README with detailed documentation:

- [Lambda Module](./modules/lambda/README.md)
- [API Gateway Module](./modules/api_gateway/README.md)
- [CloudFront Module](./modules/cloudfront/README.md)
- [DynamoDB Module](./modules/dynamodb/README.md)

## Troubleshooting

### Lambda Function Issues

Check CloudWatch Logs:
```bash
aws logs tail /aws/lambda/hokkaido-nandoku-quiz --follow
```

### Terraform State Issues

If state is corrupted or locked:
```bash
# View state
terraform show

# Force unlock (use with caution)
terraform force-unlock LOCK_ID
```

## Contributing

When making changes to the Terraform configuration:

1. Format the code: `terraform fmt -recursive`
2. Validate the configuration: `terraform validate`
3. Run a plan: `terraform plan`
4. Test in a separate environment before production

## License

See the main repository [LICENSE](../LICENSE) file.
