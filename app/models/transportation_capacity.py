from sqlalchemy import Column, Integer
from sqlalchemy.dialects.mssql import CHAR
from sqlalchemy.types import DECIMAL
from app.db.base import Base

class TransportationCapacity(Base):
    """
    運送会社キャパシティマスタ
    Transportation Company Capacity Master
    """
    __tablename__ = "HAN10M008UNSO_CAPACITY"

    HANM008001 = Column("HANM008001", CHAR(8), primary_key=True, nullable=False)  # 運送会社コード
    HANM008002 = Column("HANM008002", DECIMAL(10, 0), nullable=False)  # 限度才数
    HANM008003 = Column("HANM008003", DECIMAL(10, 0), nullable=False)  # 最大重量（kg）
    HANM008004 = Column("HANM008004", DECIMAL(3, 0), nullable=True)   # 才数換算重量（kg）
