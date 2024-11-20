import math
from operator import or_
from typing import Optional
import uuid
from sqlalchemy.orm import Session
from app.models.category import Category
from app.schemas.category import CategoryCreate,CategoryResponseList
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError


def get_category_by_name(db: Session, category_name: str):
    """Récupère une catégorie par son nom."""
    return db.query(Category).filter(
        Category.name == category_name,
        Category.is_deleted == False
    ).first()


def get_category_by_uuid(db: Session, category_uuid: str):
    """Récupère une catégorie par son UUID."""
    return db.query(Category).filter(
        Category.uuid == category_uuid,
        Category.is_deleted == False
    ).first()


def create_category(db: Session, obj_in: CategoryCreate):
    """Crée une nouvelle catégorie."""
    # Vérifier si le nom existe déjà
    db_category = get_category_by_name(db, obj_in.name)
    if db_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le nom de la catégorie existe déjà."
        )
    
    # Créer une nouvelle catégorie
    new_category = Category(
        uuid=str(uuid.uuid4()),
        name=obj_in.name
    )
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

def get_mutli(
    db: Session,
    page: int = 1,
    per_page: int = 30,
    order: Optional[str] = None,
    order_filed: Optional[str] = None,
    keyword: Optional[str] = None
):
    # Assurez-vous que la page est toujours >= 1
    if page < 1:
        page = 1
    record_query = db.query(Category).filter(Category.is_deleted == False)
    
    # Filtrer par mot-clé
    if keyword:
        record_query = record_query.filter(
            Category.name.ilike(f"%{keyword}%")
        )
    
    # Tri
    if order == "asc":
        record_query = record_query.order_by(getattr(Category, order_filed).asc())
    else:
        record_query = record_query.order_by(getattr(Category, order_filed).desc())

    total = record_query.count()
    
    # Paginer
    record_query = record_query.offset((page - 1) * per_page).limit(per_page)
    
    return CategoryResponseList(
        total=total,
        pages=math.ceil(total / per_page),  # Corrigé ici
        per_page=per_page,
        current_page=page,
        data=record_query
    )

def delete(db: Session, uuids: list[str]) -> None:
    """Supprime (désactive) les catégories par leur UUID."""
    uuids = set(uuids)  # Éviter les doublons
    categories = db.query(Category).filter(
        Category.uuid.in_(uuids),
        Category.is_deleted == False
    ).all()

    if len(categories) != len(uuids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Certaines catégories n'ont pas été trouvées."
        )

    # Marquer les catégories comme supprimées
    for category in categories:
        category.is_deleted = True

    db.commit()  # Enregistrez les modifications dans la base de données
