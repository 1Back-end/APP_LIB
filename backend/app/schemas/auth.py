from pydantic import BaseModel, ConfigDict, EmailStr
from typing import List, Optional
from datetime import datetime

class AdminBase(BaseModel):
    email: EmailStr
    phone_number: str
    username: str
    hashed_password: str

class AdminCreate(AdminBase):
    pass

class AdminUpdate(BaseModel):
    email: Optional[EmailStr]
    phone_number: Optional[str]
    username: Optional[str]
    hashed_password: Optional[str]

class AdminResponse(BaseModel):
    uuid: str
    email: EmailStr
    phone_number: str
    username: str
    role: str
    is_deleted: bool
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)

class AdminResponseList(BaseModel):
    total: int
    pages: int   # Correctement défini ici
    per_page: int
    current_page: int
    data: List[AdminResponse]

    model_config = ConfigDict(from_attributes=True)

class AdminDelete(BaseModel):
    uuids: List[str]
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


# Modèle d'authentification Admin avec Token
class AdminAuthentication(BaseModel):
    admin: AdminResponse  # Utilise 'admin' au lieu de 'Admin'
    token: Optional[Token] = None
    model_config = ConfigDict(from_attributes=True)