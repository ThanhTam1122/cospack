from sqlalchemy import Column, Integer
from sqlalchemy.types import DECIMAL
from sqlalchemy.dialects.mssql import NVARCHAR
from app.db.base import Base

class TransportationArea(Base):
    """
    Transportation Area Master
    """
    __tablename__ = "HAN10M005UNSO_AREA"

    HANM004001 = Column("HANM004001", Integer, primary_key=True, nullable=False)
    HANM004002 = Column("HANM004002", NVARCHAR(64), nullable=False)
    HANM004003 = Column("HANM004003", DECIMAL(10, 2), nullable=True)
