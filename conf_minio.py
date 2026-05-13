import os
from minio import Minio


client = Minio(
    "s3.kamaldinovnt.ru",          # без http://
    access_key=os.environ["MINIO_ROOT_USER"],
    secret_key=os.environ["MINIO_ROOT_PASSWORD"],
    secure=True,                       # HTTPS
)


bucket = "photos"
if not client.bucket_exists(bucket):
    client.make_bucket(bucket)



# from datetime import timedelta
# d
# url = client.presigned_get_object(
#     bucket,
#     "products/b18147b35221457ca4ed031a28a47092.jpg",
#     expires=timedelta(hours=2),
# )