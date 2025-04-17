from sqlalchemy import Column, Integer, String, DECIMAL
from sqlalchemy.dialects.mssql import CHAR
from app.db.base import Base

class TransportationFee(Base):
    """
    運送料金マスタ
    Transportation Fee Master
    """
    __tablename__ = "HAN10M007UNSO_FEE"

    id = Column(Integer, primary_key=True, autoincrement=True)
    HANM007001 = Column("HANM007001", Integer, nullable=False)  # 運送会社コード
    HANM007002 = Column("HANM007002", Integer, nullable=False)  # 運送エリアコード
    HANM007003 = Column("HANM007003", Integer, nullable=True)   # 最大重量（kg）

    HANM007004 = Column("HANM007004", Integer, nullable=True)   # 最大才数
    HANM007005 = Column("HANM007005", Integer, nullable=True)   # 最大サイズ（cm）
    HANM007006 = Column("HANM007006", Integer, nullable=True)   # 才数単価
    HANM007007 = Column("HANM007007", Integer, nullable=True)   # マイナス才数
    HANM007008 = Column("HANM007008", DECIMAL(10, 2), nullable=True)  # 基準額
    HANM007009 = Column("HANM007009", String(20), nullable=False)     # 料金タイプ（才数単価／固定額／個口ごと）
