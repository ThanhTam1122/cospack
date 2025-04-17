from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.dialects.mssql import CHAR
from app.db.base import Base

class TransportationAreaJISMapping(Base):
    """
    運送エリア住所コード紐付けマスタ
    Transportation Area to JIS Address Code Mapping Master
    """
    __tablename__ = "HAN10M006UNSO_AREA_JIS"

    HANM007001 = Column("HANM007001", Integer, ForeignKey("HAN10M005UNSO_AREA.HANM004001"), primary_key=True, nullable=False)  # 運送エリアコード
    HANM007002 = Column("HANM007002", CHAR(5), primary_key=True, nullable=False)  # JIS規格住所コード
