from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(BaseModel):
    name:str
    date_added: datetime
    date_modified: datetime

    # Configuration pour permettre l'utilisation des ORM
    model_config = ConfigDict(from_attributes=True)

class CategoryDelete(BaseModel):
    uuid: list[str]


class CategoryResponseList(BaseModel):
    total: int
    pages: int   # Correctement défini ici
    per_page: int
    current_page: int
    data: List[CategoryResponse]

    model_config = ConfigDict(from_attributes=True)