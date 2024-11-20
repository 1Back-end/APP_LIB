from typing import List, Optional
from fastapi import APIRouter, Body, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.category import CategoryBase,CategoryCreate,CategoryResponse
from app.crud.category_crud import create_category,get_mutli,delete
from app.schemas.msg import Msg

router = APIRouter()

@router.post("/",response_model=CategoryResponse,status_code=status.HTTP_201_CREATED)
def create(obj_in: CategoryCreate, db: Session = Depends(get_db)):
    return create_category(db, obj_in)

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
    return get_mutli(
        db, 
        page, 
        per_page, 
        order, 
        order_filed,
        keyword
    )

@router.delete("/delete", response_model=dict)
def delete_categories(
    uuids: list[str],  # Liste des UUIDs à supprimer
    db: Session = Depends(get_db)
):
    # Appel de la fonction delete pour effectuer la suppression logique
    delete(db, uuids)
    
    # Renvoyer un message de succès
    return {"detail": f"{len(uuids)} catégorie(s) supprimée(s) avec succès."}