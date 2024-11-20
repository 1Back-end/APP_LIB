from typing import List, Optional
from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.models.auth import Admin, AdminRole
from app.schemas.auth import AdminCreate, AdminUpdate, AdminResponse,AdminAuthentication
from app.crud.auth_crud import create_admin,update_admin,delete_admins,get_multiple,authenticate_super_admin,authenticate_admin
from app.database.database import get_db
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.auth import Token
from app.security.password import create_access_token,get_current_user
from datetime import timedelta
from app.security.config import ACCESS_TOKEN_EXPIRE_MINUTES



router = APIRouter()



@router.post("/login/super_admin", response_model=AdminAuthentication)
def login(
    phone_number: str = Body(...),  # Récupère le numéro de téléphone
    password: str = Body(...),      # Récupère le mot de passe
    db: Session = Depends(get_db),  # Dépendance pour obtenir la session de la base de données
):
    db_admin = authenticate_super_admin(db, phone_number=phone_number, password=password)
    
    # Génération du token d'accès
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": db_admin.email}, expires_delta=access_token_expires)
    
    return {
        "admin": db_admin,  # L'admin authentifié
        "token": {
            "access_token": access_token,
            "token_type": "bearer"
        }
    }

@router.post("/login/admin", response_model=AdminAuthentication)
def login(
    phone_number: str = Body(...),  # Récupère le numéro de téléphone
    password: str = Body(...),      # Récupère le mot de passe
    db: Session = Depends(get_db),  # Dépendance pour obtenir la session de la base de données
):
    db_admin = authenticate_admin(db, phone_number=phone_number, password=password)
    
    # Génération du token d'accès
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": db_admin.email}, expires_delta=access_token_expires)
    
    return {
        "admin": db_admin,  # L'admin authentifié
        "token": {
            "access_token": access_token,
            "token_type": "bearer"
        }
    }
# Créer un administrateur
@router.post("/", response_model=AdminResponse)
def create(
    admin: AdminCreate,  # Les données de l'administrateur à créer
    db: Session = Depends(get_db),  # Session de base de données
    # current_user: Admin = Depends(get_current_user)  # Utilisateur actuellement connecté
):
    # Vérification du rôle du `current_user` (par exemple, vérifier si c'est un SUPER_ADMIN)
    # if current_user.role != AdminRole.SUPER_ADMIN:
    #     raise HTTPException(status_code=403, detail="Accès interdit. Seul un SUPER_ADMIN peut créer un administrateur.")
    
    # Appel de la fonction pour créer l'administrateur en passant `current_user`
    return create_admin(db=db, admin_create=admin)




@router.get("/", response_model=None)
def get(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 30,
    order: str = Query("desc", enum =["asc", "desc"]),
    order_filed: str = "date_added",
    keyword: Optional[str] = None,
):
    return get_multiple(
        db, 
        page, 
        per_page, 
        order, 
        order_filed,
        keyword
    )

# Mettre à jour un administrateur
@router.put("/{uuid}", response_model=AdminResponse)
def update(uuid: str, admin: AdminUpdate, db: Session = Depends(get_db)):
    return update_admin(db=db, uuid=uuid, admin_update=admin)

# Supprimer un administrateur@router.delete("/admins/", status_code=status.HTTP_200_OK)

@router.delete("/delete", response_model=dict, status_code=status.HTTP_202_ACCEPTED)
def delete(uuids: List[str], db: Session = Depends(get_db)):
    deleted_count = delete_admins(db=db, uuid=uuids)
    return {"detail": f"{deleted_count} administrateur(s) supprimé(s) avec succès."}
