from sqlalchemy import Column, Integer, String, Float, DateTime, func
from sqlalchemy.dialects.mssql import NVARCHAR, DATETIME2
from app.db.base import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(NVARCHAR(255), index=True)
    description = Column(NVARCHAR(1000), nullable=True)
    price = Column(Float)
    created_at = Column(DATETIME2, server_default=func.now())
    updated_at = Column(DATETIME2, server_default=func.now(), onupdate=func.now()) 