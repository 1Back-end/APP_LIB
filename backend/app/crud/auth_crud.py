import math
from operator import or_
import re
from typing import List, Optional
import uuid
from sqlalchemy.orm import Session
from app.models.auth import Admin, AdminRole
from app.schemas.auth import AdminCreate, AdminUpdate,AdminResponseList
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from app.security.password import hash_password,verify_password




def get_admin_by_uuid(db:Session,admin_uuid:str):
    return db.query(Admin).filter(Admin.uuid == admin_uuid,Admin.is_deleted==False).first()

def get_admin_by_email(db:Session,admin_email:str):
    return db.query(Admin).filter(Admin.email == admin_email, Admin.is_deleted == False).first()

def get_admin_by_phone_number(db: Session, admin_phone_number: str):
    return db.query(Admin).filter(Admin.phone_number == admin_phone_number, Admin.is_deleted == False).first()
# Création d'un administrateur
def create_admin(db: Session, admin_create: AdminCreate):
    # Vérification de l'existence d'un administrateur avec le même email
    db_admin_mail = get_admin_by_email(db, admin_create.email)
    if db_admin_mail is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="L'email est déjà utilisé")
    
    # Vérification de l'existence d'un administrateur avec le même numéro de téléphone
    db_admin_phone = get_admin_by_phone_number(db, admin_create.phone_number)
    if db_admin_phone is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Le numéro de téléphone est déjà utilisé")
    
    # Vérification de la validité du numéro de téléphone
    phone_regex = r"^\+237\d{9}$"
    if not re.match(phone_regex, admin_create.phone_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Le numéro de téléphone doit commencer par +237 et contenir 9 chiffres"
        )
    
    # Vérification de la validité du mot de passe
    if len(admin_create.hashed_password) < 8:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Le mot de passe doit contenir au moins 8 caractères")
    
    # Hachage du mot de passe
    hashed_password = hash_password(admin_create.hashed_password)

    # Création de l'administrateur
    db_admin = Admin(
        uuid=str(uuid.uuid4()),  # UUID généré sous forme de chaîne
        email=admin_create.email,
        username=admin_create.username,
        phone_number=admin_create.phone_number,
        hashed_password=hashed_password  # Utilisation du mot de passe haché
    )
    
    # Ajout à la base de données et confirmation
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

def get_multiple(
        db: Session,
        page: int = 1,
        per_page: int = 30,
        order: Optional[str] = None,
        order_filed: Optional[str] = None,
        keyword: Optional[str] = None
):
    if page < 1:
        page = 1

    record_query = db.query(Admin).filter(Admin.is_deleted == False)

    # Filtrer par mot-clé
    if keyword:
        record_query = record_query.filter(
            or_(
                Admin.email.ilike(f'%{keyword}%'),
                Admin.username.ilike(f'%{keyword}%'),
                Admin.phone_number.ilike(f'%{keyword}%')
            )
        )

    # Tri
    if order and order_filed and hasattr(Admin, order_filed):
        if order == "asc":
            record_query = record_query.order_by(getattr(Admin, order_filed).asc())
        else:
            record_query = record_query.order_by(getattr(Admin, order_filed).desc())

    total = record_query.count()

    # Pagination
    record_query = record_query.offset((page - 1) * per_page).limit(per_page).all()

    return AdminResponseList(
        total=total,
        pages=math.ceil(total / per_page),
        per_page=per_page,
        current_page=page,
        data=record_query
    )


# Mise à jour d'un administrateur
def update_admin(db: Session, uuid: str, admin_update: AdminUpdate):
    db_admin = db.query(Admin).filter(Admin.uuid == uuid, Admin.is_deleted == False).first()
    if db_admin is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Administrateur non trouvé ou supprimé"
        )
    
    for key, value in admin_update.dict(exclude_unset=True).items():
        setattr(db_admin, key, value)

    db.commit()
    db.refresh(db_admin)
    return db_admin


def delete_admins(db: Session, uuid: List[str]) -> int:
    db_admins = db.query(Admin).filter(Admin.uuid.in_(uuid), Admin.is_deleted == False).all()
    if not db_admins:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aucun administrateur trouvé ou supprimé")
    
    for db_admin in db_admins:
        db_admin.is_deleted = True
        db.add(db_admin)
        db.commit()
    
    return len(db_admins)  # Retourne le nombre d'admins supprimés

    
def authenticate_super_admin(db: Session, phone_number: str, password: str) -> Optional[Admin]:
    # Recherche de l'administrateur par numéro de téléphone
    db_obj = db.query(Admin).filter(Admin.phone_number == phone_number).first()
    
    # Si aucun administrateur n'est trouvé
    if not db_obj:
        raise HTTPException(
            status_code=404, 
            detail="Aucun administrateur associé à ce numéro de téléphone n'a été trouvé. Veuillez vérifier vos informations de connexion."
        )
    
    # Vérification du mot de passe
    if not verify_password(password, db_obj.hashed_password):
        raise HTTPException(
            status_code=401, 
            detail="Le mot de passe fourni est incorrect. Veuillez réessayer."
        )
    
    # Vérification si le compte est supprimé
    if db_obj.is_deleted:
        raise HTTPException(
            status_code=401, 
            detail="Votre compte a été désactivé ou supprimé. Veuillez contacter l'administrateur pour plus d'informations."
        )
    
    # Vérification du rôle de l'administrateur
    if db_obj.role != AdminRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=403, 
            detail="Accès interdit. Vous n'avez pas les privilèges requis pour accéder à cette ressource."
        )
    
    return db_obj

def authenticate_admin(db: Session, phone_number: str, password: str) -> Optional[Admin]:
    # Recherche de l'administrateur par numéro de téléphone
    db_obj = db.query(Admin).filter(Admin.phone_number == phone_number).first()
    
    # Si aucun administrateur n'est trouvé
    if not db_obj:
        raise HTTPException(
            status_code=404, 
            detail="Aucun administrateur associé à ce numéro de téléphone n'a été trouvé. Veuillez vérifier vos informations de connexion."
        )
    
    # Vérification du mot de passe
    if not verify_password(password, db_obj.hashed_password):
        raise HTTPException(
            status_code=401, 
            detail="Le mot de passe fourni est incorrect. Veuillez réessayer."
        )
    
    # Vérification si le compte est supprimé
    if db_obj.is_deleted:
        raise HTTPException(
            status_code=401, 
            detail="Votre compte a été désactivé ou supprimé. Veuillez contacter l'administrateur pour plus d'informations."
        )
    
    # Vérification du rôle de l'administrateur
    if db_obj.role != AdminRole.ADMIN:
        raise HTTPException(
            status_code=403, 
            detail="Accès interdit. Vous n'avez pas les privilèges requis pour accéder à cette ressource."
        )
    
    return db_obj

