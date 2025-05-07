from sqlalchemy import Column, Integer
from sqlalchemy.types import DECIMAL
from sqlalchemy.dialects.mssql import CHAR
from app.db.base import Base

class CarrierSelectionLogDetail(Base):
    """
    選定ログ詳細マスタ
    Carrier Selection Log Detail Master
    """
    __tablename__ = "HAN10M011SENTEI_LOG_DETAIL"

    # 選定ログコード - Selection Log Code 
    HANM011001 = Column("HANM011001", CHAR(10), nullable=False) 
    
    # 商品コード - Product Code
    HANM011002 = Column("HANM011002", CHAR(25), nullable=False)
    
    # 見積サイズ（cm） - Estimated Size (cm)
    HANM011003 = Column("HANM011003", DECIMAL(8, 0), nullable=False)
    
    # 見積個口数 - Estimated Parcel Count
    HANM011004 = Column("HANM011004", DECIMAL(5, 0), nullable=False)

    ID = Column("ID", Integer, nullable=False, primary_key=True) #todo こちらも無くしたいです
