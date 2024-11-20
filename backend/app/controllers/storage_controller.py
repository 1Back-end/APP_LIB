from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.crud.storage_crud import create_storage, get_storage_by_uuid, get_all_storages, update_storage, delete_storage
from app.security.minio_client import upload_file_to_minio
from PIL import Image
from io import BytesIO
from uuid import uuid4
from app.database.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()


# Route pour télécharger un fichier
@router.post("/upload/")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        # Lire le fichier téléchargé
        contents = await file.read()

        # Charger l'image en mémoire
        img = Image.open(BytesIO(contents))

        # Générer une vignette (100x100)
        thumbnail = img.copy()
        thumbnail.thumbnail((100, 100))

        # Générer une image de taille moyenne (500x500)
        medium = img.copy()
        medium.thumbnail((500, 500))

        # Convertir les images en bytes
        thumbnail_bytes = BytesIO()
        thumbnail.save(thumbnail_bytes, format='JPEG')
        thumbnail_bytes.seek(0)

        medium_bytes = BytesIO()
        medium.save(medium_bytes, format='JPEG')
        medium_bytes.seek(0)

        # Upload des fichiers vers MinIO
        storage_uuid = str(uuid4())
        minio_thumbnail_url = upload_file_to_minio(thumbnail_bytes, f"thumbnails/{storage_uuid}.jpg")
        minio_medium_url = upload_file_to_minio(medium_bytes, f"medium/{storage_uuid}.jpg")

        # Créer une entrée dans la base de données
        storage = create_storage(
            db=db,
            file_name=file.filename,
            minio_file_name=f"{storage_uuid}.jpg",
            url=minio_thumbnail_url,
            mimetype=file.content_type,
            width=thumbnail.width,
            height=thumbnail.height,
            size=len(contents),
            thumbnail={"url": minio_thumbnail_url, "width": thumbnail.width, "height": thumbnail.height},
            medium={"url": minio_medium_url, "width": medium.width, "height": medium.height},
        )

        return {"message": "File uploaded successfully", "uuid": storage.uuid, "thumbnail_url": minio_thumbnail_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")

# Route pour obtenir un fichier spécifique par son UUID
@router.get("/storage/{storage_uuid}")
def get_storage(storage_uuid: str, db: Session = Depends(get_db)):
    storage = get_storage_by_uuid(db=db, storage_uuid=storage_uuid)
    if not storage:
        raise HTTPException(status_code=404, detail="Storage not found")
    return storage

# Route pour obtenir tous les fichiers avec possibilité de pagination
@router.get("/storages/")
def get_storages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    storages = get_all_storages(db=db, skip=skip, limit=limit)
    return storages

# Route pour mettre à jour les données d'un fichier
@router.put("/storage/{storage_uuid}")
async def update_storage_data(storage_uuid: str, file: UploadFile = File(None), db: Session = Depends(get_db)):
    try:
        # Si un fichier est fourni, mettre à jour avec ce nouveau fichier
        if file:
            # Lire le fichier téléchargé
            contents = await file.read()

            # Charger l'image en mémoire
            img = Image.open(BytesIO(contents))

            # Générer une vignette (100x100)
            thumbnail = img.copy()
            thumbnail.thumbnail((100, 100))

            # Générer une image de taille moyenne (500x500)
            medium = img.copy()
            medium.thumbnail((500, 500))

            # Convertir les images en bytes
            thumbnail_bytes = BytesIO()
            thumbnail.save(thumbnail_bytes, format='JPEG')
            thumbnail_bytes.seek(0)

            medium_bytes = BytesIO()
            medium.save(medium_bytes, format='JPEG')
            medium_bytes.seek(0)

            # Upload des fichiers vers MinIO
            storage_uuid = str(uuid4())
            minio_thumbnail_url = upload_file_to_minio(thumbnail_bytes, f"thumbnails/{storage_uuid}.jpg")
            minio_medium_url = upload_file_to_minio(medium_bytes, f"medium/{storage_uuid}.jpg")

            # Mettre à jour les données dans la base
            storage = update_storage(
                db=db,
                storage_uuid=storage_uuid,
                file_name=file.filename,
                minio_file_name=f"{storage_uuid}.jpg",
                url=minio_thumbnail_url,
                mimetype=file.content_type,
                width=thumbnail.width,
                height=thumbnail.height,
                size=len(contents),
                thumbnail={"url": minio_thumbnail_url, "width": thumbnail.width, "height": thumbnail.height},
                medium={"url": minio_medium_url, "width": medium.width, "height": medium.height},
            )
        else:
            # Si aucun fichier n'est fourni, simplement mettre à jour d'autres attributs
            storage = update_storage(db=db, storage_uuid=storage_uuid)

        if not storage:
            raise HTTPException(status_code=404, detail="Storage not found")
        
        return {"message": "Storage updated successfully", "storage": storage}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")

# Route pour supprimer un fichier spécifique par son UUID
@router.delete("/storage/{storage_uuid}")
def delete_storage_data(storage_uuid: str, db: Session = Depends(get_db)):
    try:
        success = delete_storage(db=db, storage_uuid=storage_uuid)
        if not success:
            raise HTTPException(status_code=404, detail="Storage not found")
        
        return {"message": "Storage deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")
