from datetime import datetime
from typing import Optional
from fastapi import HTTPException
import uuid
from sqlalchemy.orm import Session
from app.security.password import hash_password,verify_password
from sqlalchemy.exc import SQLAlchemyError
from app.models.users import User
from app.schemas.users import UserCreate, UserUpdate

def create_user(db: Session, user_data: UserCreate):
    # Vérification de l'existence de l'email avec is_deleted = False
    db_email = db.query(User).filter(User.email == user_data.email, User.is_deleted == False).first()
    if db_email:
        raise HTTPException(status_code=400, detail="Email already registered or deleted.")
    
    # Vérification de l'existence du numéro de téléphone avec is_deleted = False
    db_phone_number = db.query(User).filter(User.phone_number == user_data.phone_number, User.is_deleted == False).first()
    if db_phone_number:
        raise HTTPException(status_code=400, detail="Phone number already registered or deleted.")
    
    # Hachage du mot de passe
    hashed_password = hash_password(user_data.password)
    
    # Création de l'utilisateur
    new_user = User(
        uuid=str(uuid.uuid4()),  # UUID généré sous forme de chaîne
        username = user_data.username,
        email=user_data.email,
        phone_number=user_data.phone_number,
        hashed_password=hashed_password,  # Utilisez hashed_password pour le mot de pass
    )
    
    # Ajouter l'utilisateur à la base de données
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user  # Retourne l'utilisateur avec UUID sous forme de chaîne


def update_user(db: Session, user_uuid: str, user_data: UserUpdate):
    # Récupérer l'utilisateur de la base de données
    db_user = db.query(User).filter(User.uuid == user_uuid, User.is_deleted == False).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    # Mise à jour des informations si elles sont fournies
    db_user.username = user_data.username if user_data.username else db_user.username
    db_user.email = user_data.email if user_data.email else db_user.email
    db_user.phone_number = user_data.phone_number if user_data.phone_number else db_user.phone_number
    # Mise à jour du mot de passe si fourni
    if user_data.password:
        hashed_password = hash_password(user_data.password)  # Hachage du mot de passe
        db_user.hashed_password = hashed_password
    
    # Mettre à jour la date de modification
    db_user.date_modified = datetime.utcnow()
    
    # Commit des modifications
    db.commit()
    db.refresh(db_user)
    return db_user  # Retourne le modèle SQLAlchemy User


def deactivate_user(db: Session, user_uuid: str):
    try:
        print("=============== Récupération de l'utilisateur ============")
        # Récupérer un seul utilisateur de la base de données
        db_user = db.query(User).filter(User.uuid == user_uuid, User.is_deleted == False).first()
        
        # Vérifier si l'utilisateur existe
        if not db_user:
            print(f"==================== Aucun utilisateur trouvé =================")
            raise HTTPException(status_code=404, detail="User not found.")
        
        # Afficher les détails de l'utilisateur récupéré
        print("==================== Utilisateur récupéré =================")
        print(f"User UUID: {db_user.uuid}, Is Active: {db_user.is_active}")
        
        # Désactiver l'utilisateur
        db_user.is_active = False
        db.commit()  # Enregistrer les changements
        db.refresh(db_user)  # Rafraîchir l'objet pour voir les mises à jour
        
        # Retourner l'utilisateur après modification
        return db_user
    
    except Exception as e:
        print(f"==================== Erreur: {str(e)} =================")
        raise HTTPException(status_code=500, detail="Internal server error")

def activate_user(db: Session, user_uuid: str):
    try:
        # Récupérer l'utilisateur par UUID
        db_user = db.query(User).filter(User.uuid == user_uuid, User.is_deleted == False).first()

        # Vérifier si l'utilisateur existe
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found.")

        # Activer l'utilisateur
        db_user.is_active = True
        db.commit()  # Enregistrer les changements
        db.refresh(db_user)  # Rafraîchir l'objet pour voir les mises à jour

        # Retourner l'utilisateur après modification
        return db_user
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
def delete_user(db: Session, user_uuid: str):
    # Récupérer l'utilisateur par UUID
    db_user = db.query(User).filter(User.uuid == user_uuid, User.is_deleted == False).first()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Marquer l'utilisateur comme supprimé (par exemple avec un champ is_deleted)
    db_user.is_deleted = True
    db.commit()  # Enregistrer les changements
    db.refresh(db_user)  # Rafraîchir l'objet pour voir les mises à jour
    
    return db_user

def authenticate_user(db: Session, phone_number: str, password: str) -> Optional[User]:
    # Recherche de l'utilisateur par son numéro de téléphone
    db_obj = db.query(User).filter(User.phone_number == phone_number).first()

    # Si aucun utilisateur n'est trouvé, on renvoie une erreur
    if not db_obj:
        raise HTTPException(status_code=404, detail="Aucun utilisateur trouvé avec ce numéro de téléphone.")
    
    # Vérification du mot de passe
    if not verify_password(password, db_obj.hashed_password):
        raise HTTPException(status_code=401, detail="Mot de passe incorrect.")
    
    # Vérification si l'utilisateur est supprimé
    if db_obj.is_deleted:
        raise HTTPException(status_code=401, detail="Votre compte a été supprimé.")
    
    # Vérification si l'utilisateur est actif
    if not db_obj.is_active:
        raise HTTPException(status_code=401, detail="Votre compte n'est pas actif.")
     
    return db_obj
