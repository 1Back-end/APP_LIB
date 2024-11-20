from minio import Minio
from minio.error import S3Error
from .config import Config

minioClient = Minio(Config.MINIO_URL,
                    access_key=Config.MINIO_ACCESS_KEY,
                    secret_key=Config.MINIO_SECRET_KEY,
                    secure=Config.MINIO_SECURE)

def upload_file(path, file_name, content_type):
    try:
        # Ensure the bucket exists, or create it
        if not minioClient.bucket_exists(Config.MINIO_BUCKET):
            minioClient.make_bucket(Config.MINIO_BUCKET)
    except S3Error as err:
        print(f"Error while checking or creating bucket: {err}")
        raise

    # Upload the file to Minio bucket
    try:
        minioClient.fput_object(Config.MINIO_BUCKET, file_name, path, content_type=content_type)
        url = minioClient.presigned_get_object(Config.MINIO_BUCKET, file_name)
        return Config.MINIO_API_URL + file_name, file_name
    except S3Error as err:
        print(f"Error while uploading file: {err}")
        return str(err)
