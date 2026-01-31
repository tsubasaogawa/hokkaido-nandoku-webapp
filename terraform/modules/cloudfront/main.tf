# CloudFront Distribution Module
# This module creates a CloudFront distribution for the API Gateway

resource "aws_cloudfront_distribution" "this" {
  origin {
    domain_name = var.origin_domain_name
    origin_id   = var.origin_id

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }

    custom_header {
      name  = var.custom_header_name
      value = var.custom_header_value
    }
  }

  enabled         = true
  is_ipv6_enabled = true
  comment         = var.comment

  # Add custom domain name (alternate domain name) if provided
  aliases = var.domain_name != "" ? [var.domain_name] : []

  default_cache_behavior {
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = var.origin_id

    viewer_protocol_policy = "redirect-to-https"

    # Managed-CachingDisabled policy
    cache_policy_id = var.cache_policy_id
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    # Use custom certificate if domain name is provided, otherwise use default CloudFront certificate
    cloudfront_default_certificate = var.domain_name == "" ? true : false
    acm_certificate_arn            = var.domain_name != "" ? var.certificate_arn : null
    ssl_support_method             = var.domain_name != "" ? "sni-only" : null
    minimum_protocol_version       = var.domain_name != "" ? "TLSv1.2_2021" : null
  }

  lifecycle {
    ignore_changes = [
      web_acl_id,
    ]
  }

  tags = var.tags
}
