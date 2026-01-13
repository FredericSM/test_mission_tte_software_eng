output "bucket_name" { value = aws_s3_bucket.data.bucket }
output "lambda_name" { value = aws_lambda_function.ingest.function_name }