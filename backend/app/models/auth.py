import datetime
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from enum import Enum
from app.database.database import Base
from sqlalchemy.sql import func
import uuid


class AdminRole(str,Enum):
    ADMIN= "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"

class Admin(Base):
    __tablename__ = "admin"
    uuid = Column(String,index=True,unique=True ,primary_key=True)
    email = Column(String, unique=True, index=True)
    username = Column(String)
    phone_number = Column(String, nullable=True)
    hashed_password = Column(String)
    role = Column(String(50), default=AdminRole.ADMIN.value,index=True)
    # is_admin = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    date_added = Column(DateTime, default=func.now())
    date_modified = Column(DateTime, default=func.now(), onupdate=func.now())