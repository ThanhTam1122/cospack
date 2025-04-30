from sqlalchemy import Column, DECIMAL, Integer
from sqlalchemy.dialects.mssql import CHAR
from app.db.base import Base

class TransportationFee(Base):
    """
    運送料金マスタ (HAN99MA12TRANSPORTATIONFEE)
    Transportation Fee Master
    """
    __tablename__ = "HAN99MA12TRANSPORTATIONFEE"
    
    # 運送会社コード - Transportation Company Code
    HANMA12001 = Column("HANMA12001", CHAR(8), nullable=False)
    
    # 運送エリアコード - Transportation Area Code
    HANMA12002 = Column("HANMA12002", CHAR(8), nullable=False)
    
    # 最大重量（kg） - Maximum Weight in kg
    HANMA12003 = Column("HANMA12003", DECIMAL(5, 0), nullable=True)
    
    # 最大才数 - Maximum Volume
    HANMA12004 = Column("HANMA12004", DECIMAL(5, 0), nullable=True)
    
    # 最大サイズ（cm） - Maximum Size in cm
    HANMA12005 = Column("HANMA12005", DECIMAL(5, 0), nullable=True)
    
    # 才数単価 - Unit Price per Volume
    HANMA12006 = Column("HANMA12006", DECIMAL(15, 0), nullable=True)
    
    # マイナス才数 - Minus Volume
    HANMA12007 = Column("HANMA12007", DECIMAL(5, 0), nullable=True)
    
    # 基準額 - Base Amount
    HANMA12008 = Column("HANMA12008", DECIMAL(15, 0), nullable=False)
    
    # 料金タイプ - Fee Type
    HANMA12009 = Column("HANMA12009", DECIMAL(1, 0), nullable=False)

    ID = Column("ID", Integer, nullable=False, primary_key=True)

    def __repr__(self):
        return f"<TransportationFee {self.HANMA12001}-{self.HANMA12002}>"
