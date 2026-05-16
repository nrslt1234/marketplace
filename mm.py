import json
import os
from minio import Minio
from dotenv import load_dotenv
load_dotenv(".env")

client = Minio(
    "s3.kamaldinovnt.ru",          # без http://
    access_key=os.environ["MINIO_ROOT_USER"],
    secret_key=os.environ["MINIO_ROOT_PASSWORD"],
    secure=True,                       # HTTPS
)


bucket = "photos"
if not client.bucket_exists(bucket):
    client.make_bucket(bucket)



policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"AWS": ["*"]},
            "Action": ["s3:GetObject"],
            "Resource": [
                f"arn:aws:s3:::{bucket}/products/*"
            ],
        }
    ],
}

client.set_bucket_policy(bucket, json.dumps(policy))
