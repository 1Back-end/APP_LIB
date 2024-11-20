from pydantic import BaseModel, ConfigDict,EmailStr
from typing import List, Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    username: str  # Permettre que 'username' soit optionnel
    phone_number: Optional[str] = None
    password: str  # Le mot de passe sera inclus uniquement lors de la création, pas dans la réponse
    # is_admin: Optional[bool] = False  # Indiquer si l'utilisateur est administrateur

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None  # Permet de mettre à jour le mot de passe
    date_modified: datetime = datetime.utcnow()


class UserResponse(BaseModel):
    uuid: str  # Assurez-vous d'avoir un champ 'uuid' pour identifier l'utilisateur
    email: str
    username: str
    phone_number: Optional[str] = None
    status : str
    is_active : bool
    # is_admin: bool
    date_added: datetime
    date_modified: datetime
    model_config = ConfigDict(from_attributes=True)

class UserDelete(BaseModel):
    uuids: List[str]

    model_config = ConfigDict(from_attributes=True)

class UserUUIDsRequest(BaseModel):
    user_uuids: List[str]

class Token(BaseModel):
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


# Modèle d'authentification Admin avec Token
class UserAuthentication(BaseModel):
    user: UserResponse  # Utilise 'admin' au lieu de 'Admin'
    token: Optional[Token] = None
    model_config = ConfigDict(from_attributes=True)
