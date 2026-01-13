import json
import os
import boto3

s3 = boto3.client("s3")
AGG_PREFIX = os.environ.get("AGG_PREFIX", "agg/")

def handler(event, context):
    record = event["Records"][0]
    bucket = record["s3"]["bucket"]["name"]
    key = record["s3"]["object"]["key"]

    print(json.dumps({
        "level": "INFO",
        "msg": "S3 event received",
        "bucket": bucket,
        "key": key,
        "request_id": context.aws_request_id
    }))

    obj = s3.get_object(Bucket=bucket, Key=key)
    body = obj["Body"].read().decode("utf-8", errors="replace")
    lines = [line for line in body.splitlines() if line.strip()]

    summary = {
        "source_bucket": bucket,
        "source_key": key,
        "rows": max(0, len(lines) - 1),
    }

    out_key = f"{AGG_PREFIX}{key.replace('raw/', '').replace('.csv','')}_summary.json"
    s3.put_object(
        Bucket=bucket,
        Key=out_key,
        Body=json.dumps(summary).encode("utf-8"),
        ContentType="application/json"
    )

    print(json.dumps({
        "level": "INFO",
        "msg": "Wrote summary",
        "out_key": out_key,
        "rows": summary["rows"]
    }))

    return {"statusCode": 200, "body": json.dumps(summary)}