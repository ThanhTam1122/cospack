from sqlalchemy import Column, Integer, String, Date, Boolean, Float
from sqlalchemy.types import DECIMAL
from sqlalchemy.dialects.mssql import NVARCHAR, CHAR, VARCHAR
from sqlalchemy.sql.expression import text
from app.db.base import Base

class TransportationCompanyMaster(Base):
    """
    運送会社マスター
    Transportation Company Master
    """
    __tablename__ = "HAN99MA02UNSOU"  # Assuming table name based on the pattern
    
    # Primary key
    HANMA02001 = Column("HANMA02001", CHAR(2), primary_key=True, nullable=False, default='')  # 運送会社コード
    
    # Data fields
    HANMA02002 = Column("HANMA02002", CHAR(20), nullable=False, default='')  # 運送会社名
    HANMA02003 = Column("HANMA02003", DECIMAL(1, 0), nullable=False, default=0)  # 運送会社区分
    HANMA02004 = Column("HANMA02004", DECIMAL(1, 0), nullable=False, default=0)  # 荷札出力区分
    HANMA02005 = Column("HANMA02005", DECIMAL(8, 0), nullable=False, default=0)  # 最終貨物番号(採番部)
    HANMA02006 = Column("HANMA02006", CHAR(13), nullable=False, default='')  # 最終貨物番号
    HANMA02007 = Column("HANMA02007", DECIMAL(4, 0), nullable=False, default=0)  # CABパラメータ№(印刷用)
    HANMA02008 = Column("HANMA02008", DECIMAL(4, 0), nullable=False, default=0)  # CABパラメータ№(プレビュー用)
    HANMA02009 = Column("HANMA02009", DECIMAL(1, 0), nullable=False, default=0)  # 代引金額入力区分
    
    # System fields
    HANMA02999 = Column("HANMA02999", DECIMAL(9, 0), nullable=False, default=0)  # 更新番号
    
    def __repr__(self):
        return f"<TransportationCompanyMaster {self.HANMA02001}>" 