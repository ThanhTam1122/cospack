from sqlalchemy import Column, Integer
from app.db.base import Base

class TransportationCapacity(Base):
    """
    運送会社キャパシティマスタ
    Transportation Company Capacity Master
    """
    __tablename__ = "HAN10M008UNSO_CAPACITY"

    HANM008001 = Column("HANM008001", Integer, primary_key=True, nullable=False)  # 運送会社コード
    HANM008002 = Column("HANM008002", Integer, nullable=False)  # 限度才数
    HANM008003 = Column("HANM008003", Integer, nullable=False)  # 最大重量（kg）
    HANM008004 = Column("HANM008004", Integer, nullable=True)   # 才数換算重量（kg）
