from minio import Minio
from minio.error import S3Error
import os
import logging

def getClient ():
    client = Minio(
        os.getenv("MINIO_URL"),
        access_key=os.getenv("MINIO_ACCESS_KEY"),
        secret_key=os.getenv("MINIO_SECRET_KEY"),
        secure=False,
    )
    return client

def createBucket (client):
    found = client.bucket_exists("profiles")
    if not found:
        client.make_bucker("profiles")
        logging.info("Bucket 'profiles' created.")
    else:
        logging.info("Bucket 'profiles' already exists.")

def uploadImage (client, image_path, image_name):
    try:
        createBucket(client)
        client.fput_object(
            "profiles",
            image_name,
            image_path,
        )
        logging.info(f"Image '{image_name}' uploaded successfully to bucket 'profiles'.")
    except S3Error as e:
        logging.error(f"Error uploading image '{image_name}': {e}")
    except Exception as e:
        logging.error(f"Unexpected error occured: {e}")

