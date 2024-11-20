# app/minio_client.py
from minio import Minio
from minio.error import S3Error
import os
from io import BytesIO

# Configuration de MinIO
MINIO_URL = "127.0.0.1:9000"  # Remplacez par l'URL de votre instance MinIO
MINIO_ACCESS_KEY = "newuser"  # Remplacez par votre clé d'accès MinIO
MINIO_SECRET_KEY = "newpassword"  # Remplacez par votre clé secrète MinIO
MINIO_BUCKET_NAME = "your-bucket-name"  # Remplacez par votre nom de bucket

# Initialisation du client MinIO
client = Minio(
    MINIO_URL,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False  # Mettre à True si vous utilisez HTTPS
)

def upload_file_to_minio(file: BytesIO, object_name: str) -> str:
    """
    Télécharge un fichier vers MinIO.

    :param file: Fichier à télécharger sous forme de BytesIO.
    :param object_name: Nom de l'objet (le nom sous lequel le fichier sera stocké dans MinIO).
    :return: URL du fichier téléchargé dans MinIO.
    """
    try:
        # Télécharger le fichier dans le bucket MinIO
        client.put_object(
            MINIO_BUCKET_NAME,
            object_name,
            file,
            len(file.getvalue())
        )
        
        # Retourner l'URL de l'objet (si votre MinIO est configuré pour cela)
        file_url = f"http://{MINIO_URL}/{MINIO_BUCKET_NAME}/{object_name}"
        return file_url
    except S3Error as e:
        raise Exception(f"Error uploading file to MinIO: {str(e)}")
