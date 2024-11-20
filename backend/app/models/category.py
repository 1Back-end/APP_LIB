import datetime
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from enum import Enum
from app.database.database import Base

class Category(Base):
    __tablename__ = "categories"
    uuid = Column(String,index=True,unique=True ,primary_key=True)
    name = Column(String, unique=True, nullable=False)
    is_deleted = Column(Boolean, default=False)
    date_added: datetime = Column(DateTime, nullable=False, default=datetime.datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.datetime.now())