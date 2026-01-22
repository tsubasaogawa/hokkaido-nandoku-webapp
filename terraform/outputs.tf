output "cloudfront_url" {
  description = "The URL of the CloudFront Distribution."
  value       = aws_cloudfront_distribution.cf_dist.domain_name
}
