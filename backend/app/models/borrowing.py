import datetime
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from enum import Enum
from app.database.database import Base
from .category import Category
from .users import User
from .book import Book

class Borrowing(Base):
    __tablename__ = "borrowings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"))
    book_uuid = Column(UUID(as_uuid=True), ForeignKey("books.uuid"))
    borrowed_at = Column(DateTime, nullable=False)
    returned_at = Column(DateTime, nullable=True)