# app/utils.py
from random import choice, randint, random
import string
from typing import Dict
import bcrypt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from requests import Session
from app.models.auth import Admin
from app.security.config import SECRET_KEY, ALGORITHM
from app.database.database import get_db
from typing import List, Optional
from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
import jwt

# Créez un contexte pour bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hacher un mot de passe
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Vérifier un mot de passe
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta if expires_delta else datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise Exception("Token invalid or expired")
    
def generate_code(length=10):
    """Generate a random string of fixed length """

    end = random.choice([True, False])

    string_length = round(length / 3)
    letters = string.ascii_lowercase
    random_string = (''.join(choice(letters) for i in range(string_length))).upper()
    range_start = 10 ** ((length - string_length) - 1)
    range_end = (10 ** (length - string_length)) - 1
    random_number = randint(range_start, range_end)
    if not end:
        final_string = f"{random_string}{random_number}"
    else:
        final_string = f"{random_number}{random_string}"
    return final_string


def decode_access_token(token: str):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_token
    except Exception as e:
        if token:
            print("Failed to decode token")
            print(token)
            print(e)
        return None

# Fonction pour décoder et vérifier le JWT
def decode_jwt_token(token: str) -> Dict:
    try:
        # Décoder le token avec la clé secrète et l'algorithme spécifié
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Vérification de la date d'expiration du token
        if datetime.utcfromtimestamp(payload["exp"]) < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Token expiré.")

        return payload  # Retourner les données décodées du token, comme l'email de l'administrateur

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré.")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Token invalide.")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Fonction pour vérifier le token (par exemple, décodez-le avec JWT)
def verify_token(token: str) -> dict:
    # Implémenter ici la logique pour vérifier et décoder le token JWT
    # Exemple : Utiliser JWT pour décoder le token et obtenir les informations de l'administrateur
    try:
        # Implémentation fictive du décodage du token, à adapter à votre logique de vérification
        return decode_jwt_token(token)  # Fonction pour décoder le JWT et récupérer les données
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré.")

# Fonction pour obtenir l'utilisateur actuel à partir du token
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> Admin:
    try:
        # Vérifiez et extrayez les informations du token
        admin_data = verify_token(token)  # Cette fonction décode le token et récupère les données de l'admin
        db_admin = db.query(Admin).filter(Admin.email == admin_data["sub"]).first()

        if not db_admin:
            raise HTTPException(status_code=404, detail="Administrateur non trouvé.")
        
        return db_admin
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré.")