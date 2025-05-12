from sqlalchemy import Column, Integer, CHAR
from sqlalchemy import PrimaryKeyConstraint
from app.db.base import Base

class TransportationAreaJISMapping(Base):
    """
    運送エリア住所コード紐付けマスタ (HAN99MA11AREAJIS)
    Transportation Area to JIS Code Mapping
    """
    __tablename__ = "HAN99MA11AREAJIS"
    
    # 運送エリアコード - Transportation Area Code
    HANMA11001 = Column("HANMA11001", Integer, nullable=False)
    
    # JIS規格住所コード - JIS Standard Address Code
    HANMA11002 = Column("HANMA11002", CHAR(5), nullable=False)

    # Composite Primary Key
    __table_args__ = (
        PrimaryKeyConstraint('HANMA11001', 'HANMA11002', name='pk_transportation_area_jis'),
    )

    def __repr__(self):
        return f"<TransportationAreaJISMapping {self.HANMA11002} -> {self.HANMA11001}>"