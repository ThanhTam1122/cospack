from sqlalchemy import Column, DECIMAL
from sqlalchemy.dialects.mssql import CHAR
from app.db.base import Base

class SpecialCapacity(Base):
    """
    特殊キャパシティマスタ (HAN99MA15SPECIALCAPACITY)
    Special Capacity Master
    """
    __tablename__ = "HAN99MA15SPECIALCAPACITY"
    
    # 運送会社コード - Transportation Company Code
    HANMA15001 = Column("HANMA15001", CHAR(8), primary_key=True, nullable=False)
    
    # 都道府県コード - Prefecture Code
    HANMA15002 = Column("HANMA15002", CHAR(2), primary_key=True, nullable=False)
    
    # 日付 - Date (YYYYMMDD format)
    HANMA15003 = Column("HANMA15003", CHAR(8), primary_key=True, nullable=False)
    
    # 運送能力(件数) - Transportation Capacity (Number of Cases)
    HANMA15004 = Column("HANMA15004", DECIMAL(5, 0), nullable=False)
    
    # 残り件数 - Remaining Number of Cases
    HANMA15005 = Column("HANMA15005", DECIMAL(5, 0), nullable=False)

    def __repr__(self):
        return f"<SpecialCapacity {self.HANMA15001}-{self.HANMA15002}-{self.HANMA15003}>" 