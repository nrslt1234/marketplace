import os
from minio import Minio


client = Minio(
    "s3.kamaldinovnt.ru:9000",          # без http://
    access_key=os.environ["MINIO_ROOT_USER"],
    secret_key=os.environ["MINIO_ROOT_PASSWORD"],
    secure=True,                       # HTTPS
)


bucket = "photos"
if not client.bucket_exists(bucket):
    client.make_bucket(bucket)