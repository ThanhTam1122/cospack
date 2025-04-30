from sqlalchemy import Column
from sqlalchemy.dialects.mssql import CHAR
from sqlalchemy.types import DECIMAL
from app.db.base import Base

class SpecialCapacity(Base):
    """
    特殊キャパシティマスタ (HAN99MA15SPECIALCAPACITY)
    Special Capacity Master
    """
    __tablename__ = "HAN99MA15SPECIALCAPACITY"
    
    # 運送会社コード - Transportation Company Code
    HANMA15001 = Column("HANMA15001", CHAR(8), primary_key=True, nullable=False)
    
    # 出荷日 - Shipping Date (YYYYMMDD format)
    HANMA15002 = Column("HANMA15002", DECIMAL(8, 0), primary_key=True, nullable=False)
    
    # 限度才数 - Volume Capacity Limit
    HANMA15003 = Column("HANMA15003", DECIMAL(10, 0), nullable=False)
    
    # 最大重量（kg） - Maximum Weight (kg)
    HANMA15004 = Column("HANMA15004", DECIMAL(10, 0), nullable=False)

    def __repr__(self):
        return f"<SpecialCapacity {self.HANMA15001}-{self.HANMA15002}>" 