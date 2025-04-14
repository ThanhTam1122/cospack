from sqlalchemy import Column, Integer, ForeignKey
from app.db.base import Base

class CarrierSelectionLogDetail(Base):
    """
    選定ログ詳細マスタ
    Carrier Selection Log Detail Master
    """
    __tablename__ = "HAN10M011SENTEI_LOG_DETAIL"

    HANM011001 = Column("HANM011001", Integer, ForeignKey("HAN10M010SENTEI_LOG.HANM010001"), primary_key=True)  # 選定ログコード（親と連携）
    HANM011002 = Column("HANM011002", Integer, primary_key=True)  # 商品コード（複合PKの一部）
    HANM011003 = Column("HANM011003", Integer, nullable=False)  # 見積サイズ（cm）
    HANM011004 = Column("HANM011004", Integer, nullable=False)  # 見積個口数
