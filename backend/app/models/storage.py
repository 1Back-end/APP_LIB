# app/models/storage.py
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from uuid import uuid4
from app.database.database import Base

class Storage(Base):
    """ Storage Model for storing file-related details in the database """

    __tablename__ = "storages"

    uuid: str = Column(String, index=True, unique=True, primary_key=True)
    file_name: str = Column(Text, default="", nullable=True)
    minio_file_name: str = Column(Text, default="", nullable=True)  # File name on MinIO
    url: str = Column(Text, default="", nullable=True)  # URL of the image or file
    mimetype: str = Column(Text, default="", nullable=True)  # Mime type (e.g., image/jpeg)

    width: int = Column(Integer, default=0, nullable=True)
    height: int = Column(Integer, default=0, nullable=True)
    size: int = Column(Integer, default=0, nullable=True)  # Size in bytes

    thumbnail: JSON = Column(JSON, default={}, nullable=True)  # Thumbnail data
    medium: JSON = Column(JSON, default={}, nullable=True)  # Medium resolution image

    date_added: DateTime = Column(DateTime, server_default=func.now())
    date_modified: DateTime = Column(DateTime, server_default=func.now(), onupdate=func.now())
