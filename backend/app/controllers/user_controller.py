from typing import List
from fastapi import APIRouter, Body, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.users import UserCreate, UserUpdate,UserResponse,UserUUIDsRequest,UserAuthentication
from app.crud.user_crud import create_user, update_user, activate_user, deactivate_user,delete_user,authenticate_user
from app.schemas.msg import Msg
from app.security.password import create_access_token
from datetime import timedelta
from app.security.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.schemas.users import Token
router = APIRouter()


@router.post('/login', response_model=UserAuthentication)
def login_with_phone_number_password(
    phone_number: str = Body(...),  # Récupère le numéro de téléphone du corps de la requête
    password: str = Body(...),      # Récupère le mot de passe du corps de la requête
    db: Session = Depends(get_db),  # Dépendance pour obtenir la session de la base de données
):
    # Authentifie l'utilisateur en vérifiant le numéro de téléphone et le mot de passe
    db_user = authenticate_user(db, phone_number=phone_number, password=password)
    
    # Génère le token d'accès
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": db_user.email}, expires_delta=access_token_expires)
    
    # Construction de la réponse
    return UserAuthentication(
        user=db_user,  # L'utilisateur authentifié
        token=Token(
            access_token=access_token,
            token_type="bearer"
        )
    )



@router.post('/', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create(user_data: UserCreate, db: Session = Depends(get_db)):
    user = create_user(db, user_data)
    return user  # FastAPI utilise le modèle UserResponse et convertit correctement l'UUID


@router.put("/{user_uuid}", response_model=UserResponse)
def update(user_uuid: str, user_data: UserUpdate, db: Session = Depends(get_db)):
    try:
        # Appel de la fonction pour mettre à jour l'utilisateur
        updated_user = update_user(db=db, user_uuid=user_uuid, user_data=user_data)
        return updated_user  # Retourne les données mises à jour de l'utilisateur
    except HTTPException as e:
        raise e  # Si l'utilisateur n'est pas trouvé, une exception HTTP est levée
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  # Erreur serveur générique


@router.put("/deactivate/{user_uuid}", response_model=Msg)
def deactivate(user_uuid: str, db: Session = Depends(get_db)):
    db_user = deactivate_user(db=db, user_uuid=user_uuid)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Renvoyer un message de succès
    return Msg(message="User deactivated successfully")
@router.put("/activate/{user_uuid}", response_model=Msg)
def activate(user_uuid: str, db: Session = Depends(get_db)):
    db_user = activate_user(db=db, user_uuid=user_uuid)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return Msg(message="User activated successfully")

@router.delete("/delete/{user_uuid}", response_model=Msg)
def delete(user_uuid: str, db: Session = Depends(get_db)):
    db_user = delete_user(db=db, user_uuid=user_uuid)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return Msg(message="User deleted successfully")
