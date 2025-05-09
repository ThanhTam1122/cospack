from sqlalchemy import Column, Integer
from sqlalchemy.dialects.mssql import CHAR
from app.db.base import Base

class TransportationAreaJISMapping(Base):
    """
    運送エリア住所コード紐付けマスタ (HAN99MA11AREAJIS)
    Transportation Area to JIS Code Mapping
    """
    __tablename__ = "HAN99MA11AREAJIS"
    
    # 運送エリアコード - Transportation Area Code
    HANMA11001 = Column("HANMA11001", Integer, nullable=False)
    
    # JIS規格住所コード - JIS Standard Address Code (5 digits)
    HANMA11002 = Column("HANMA11002", CHAR(5), nullable=False)

    ID = Column("ID", Integer, nullable=False, primary_key=True) #todo こちらも無くしたいです

    def __repr__(self):
        return f"<TransportationAreaJISMapping {self.HANMA11002} -> {self.HANMA11001}>"
