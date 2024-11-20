# main.py
from fastapi import FastAPI, Depends, APIRouter
from sqlalchemy.orm import Session
from app.database.database import engine, Base
from app.database.database import get_db
from app.models.users import User

router = APIRouter()
# Endpoint to create tables
@router.post("/")
def create_tables(db: Session = Depends(get_db)):
    Base.metadata.create_all(bind=engine)
    return {"message": "Tables created successfully"}

