from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status, Depends
from app.database.database import get_db
from app import models
from sqlalchemy.orm import Session
import os

# Variables de configuration pour JWT
SECRET_KEY = os.getenv("SECRET_KEY", "f105571e5f0998feba2ad5a9f17f992d38bf638457646a97902872f66912c3e3")  # Utilise une clé secrète sécurisée
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Durée de validité du token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")  # L'URL pour obtenir le token

# Fonction pour créer un token d'accès
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

