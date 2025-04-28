from sqlalchemy import Column, Integer, String, Float, DECIMAL
from sqlalchemy.dialects.mssql import NVARCHAR, CHAR
from app.db.base import Base

class TransportationArea(Base):
    """
    運送エリアマスタ (HAN99MA10TRANSPORTATIONAREA)
    Transportation Area Master
    """
    __tablename__ = "HAN99MA10TRANSPORTATIONAREA"
    
    # 運送エリアコード - Transportation Area Code
    HANMA10001 = Column("HANMA10001", CHAR(8), primary_key=True, nullable=False)
    
    # 運送エリア名 - Transportation Area Name
    HANMA10002 = Column("HANMA10002", NVARCHAR(256), nullable=False)
    
    # 距離（km） - Distance in kilometers
    HANMA10003 = Column("HANMA10003", DECIMAL(5, 0), nullable=True)

    def __repr__(self):
        return f"<TransportationArea {self.HANMA10001}>"
