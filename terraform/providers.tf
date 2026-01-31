# AWS Provider Configuration

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = local.common_tags
  }
}

# AWS Provider for us-east-1 (required for CloudFront ACM certificates)
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"

  default_tags {
    tags = local.common_tags
  }
}
