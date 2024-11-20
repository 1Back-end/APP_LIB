# app/crud/storage_crud.py
from sqlalchemy.orm import Session
from app.models.storage import Storage
from uuid import uuid4
from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError

def create_storage(db: Session, file_name: str, minio_file_name: str, url: str, mimetype: str, 
                   width: int, height: int, size: int, thumbnail: dict, medium: dict) -> Storage:
    """Crée une nouvelle entrée de stockage dans la base de données"""
    storage_uuid = str(uuid4())  # Générer un UUID unique
    new_storage = Storage(
        uuid=storage_uuid,
        file_name=file_name,
        minio_file_name=minio_file_name,
        url=url,
        mimetype=mimetype,
        width=width,
        height=height,
        size=size,
        thumbnail=thumbnail,
        medium=medium
    )
    try:
        db.add(new_storage)
        db.commit()
        db.refresh(new_storage)
        return new_storage
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def get_storage_by_uuid(db: Session, storage_uuid: str) -> Optional[Storage]:
    """Récupère un fichier de stockage par UUID"""
    return db.query(Storage).filter(Storage.uuid == storage_uuid).first()

def get_all_storages(db: Session, skip: int = 0, limit: int = 100) -> List[Storage]:
    """Récupère une liste de tous les fichiers de stockage"""
    return db.query(Storage).offset(skip).limit(limit).all()

def update_storage(db: Session, storage_uuid: str, file_name: Optional[str] = None, 
                   minio_file_name: Optional[str] = None, url: Optional[str] = None, 
                   mimetype: Optional[str] = None, width: Optional[int] = None, 
                   height: Optional[int] = None, size: Optional[int] = None,
                   thumbnail: Optional[dict] = None, medium: Optional[dict] = None) -> Optional[Storage]:
    """Met à jour une entrée de stockage"""
    storage = db.query(Storage).filter(Storage.uuid == storage_uuid).first()
    if not storage:
        return None

    # Mettre à jour les champs qui sont fournis
    if file_name: storage.file_name = file_name
    if minio_file_name: storage.minio_file_name = minio_file_name
    if url: storage.url = url
    if mimetype: storage.mimetype = mimetype
    if width: storage.width = width
    if height: storage.height = height
    if size: storage.size = size
    if thumbnail: storage.thumbnail = thumbnail
    if medium: storage.medium = medium
    
    db.commit()
    db.refresh(storage)
    return storage

def delete_storage(db: Session, storage_uuid: str) -> bool:
    """Supprime une entrée de stockage"""
    storage = db.query(Storage).filter(Storage.uuid == storage_uuid).first()
    if not storage:
        return False

    db.delete(storage)
    db.commit()
    return True
