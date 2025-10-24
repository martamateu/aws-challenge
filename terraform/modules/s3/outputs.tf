output "bucket_names" {
  description = "Names of created S3 buckets"
  value = {
    data    = aws_s3_bucket.data.id
    logs    = aws_s3_bucket.logs.id
    backups = aws_s3_bucket.backups.id
  }
}

output "bucket_arns" {
  description = "ARNs of created S3 buckets"
  value = [
    aws_s3_bucket.data.arn,
    aws_s3_bucket.logs.arn,
    aws_s3_bucket.backups.arn
  ]
}

output "data_bucket_id" {
  description = "ID of the data bucket"
  value       = aws_s3_bucket.data.id
}

output "logs_bucket_id" {
  description = "ID of the logs bucket"
  value       = aws_s3_bucket.logs.id
}

output "backups_bucket_id" {
  description = "ID of the backups bucket"
  value       = aws_s3_bucket.backups.id
}
