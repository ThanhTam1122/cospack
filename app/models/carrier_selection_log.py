from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base

class CarrierSelectionLog(Base):
    """
    選定ログマスタ
    """
    __tablename__ = "HAN10M010SENTEI_LOG"

    HANM010001 = Column("HANM010001", Integer, primary_key=True, nullable=False)  # 選定ログコード
    HANM010002 = Column("HANM010002", Integer, ForeignKey("HAN10M009OKURIJO.HANM009001"), nullable=False)  # 送り状コード
    HANM010003 = Column("HANM010003", Integer, nullable=False)  # 見積個口数
    HANM010004 = Column("HANM010004", Integer, nullable=False)  # 見積才数
    HANM010005 = Column("HANM010005", Integer, nullable=False)  # 見積重量（kg）
    HANM010006 = Column("HANM010006", Integer, nullable=False)  # 最安運送会社コード
    HANM010007 = Column("HANM010007", Integer, nullable=False)  # 選定運送会社コード
    HANM010008 = Column("HANM010008", String(128), nullable=True)  # 選定理由
