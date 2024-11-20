# app/config.py
from datetime import timedelta

SECRET_KEY = "f105571e5f0998feba2ad5a9f17f992d38bf638457646a97902872f66912c3e3"  # Remplacez par une clé secrète aléatoire
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

import os

class Config:
    # Configuration MinIO
    MINIO_URL = os.getenv("MINIO_URL", "localhost:9000")  # Exemple : "localhost:9000"
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "votre_clé_minio")  # Remplacez par votre clé d'accès MinIO
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "votre_clé_secrète_minio")  # Remplacez par votre clé secrète MinIO
    MINIO_BUCKET = os.getenv("MINIO_BUCKET", "votre_nom_de_bucket")  # Remplacez par le nom de votre bucket
    MINIO_SECURE = bool(os.getenv("MINIO_SECURE", False))  # False si vous utilisez HTTP, True si vous utilisez HTTPS
    MINIO_API_URL = os.getenv("MINIO_API_URL", "http://localhost:9000/")  # URL de l'API MinIO
