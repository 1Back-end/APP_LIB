# app/models/book.py
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from datetime import datetime
from app.database.database import Base
from app.models.category import Category
from app.models.storage import Storage  # Import Storage model

class Book(Base):
    __tablename__ = "books"
    
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    category_uuid = Column(UUID(as_uuid=True), ForeignKey("categories.uuid"))
    is_available = Column(Boolean, default=True)
    category = relationship("Category")
    is_deleted = Column(Boolean, default=False)
    date_added = Column(DateTime, nullable=False, default=datetime.now())
    date_modified = Column(DateTime, nullable=False, default=datetime.now())

    # Relation avec le modèle Storage (une œuvre peut avoir une ou plusieurs images)
    storage_uuid = Column(UUID(as_uuid=True), ForeignKey("storages.uuid"))
    storage = relationship("Storage", backref="book")  # On lie chaque livre à un fichier de stockage

