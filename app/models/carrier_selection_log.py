from sqlalchemy import Column
from sqlalchemy.types import DECIMAL
from sqlalchemy.sql.expression import text
from sqlalchemy.dialects.mssql import CHAR, NVARCHAR
from app.db.base import Base

class CarrierSelectionLog(Base):
    """
    選定ログマスタ
    Carrier Selection Log Master
    """
    __tablename__ = "HAN10M010SENTEI_LOG"

    HANM010001 = Column("HANM010001", CHAR(10), primary_key=True, nullable=False)  # 選定ログコード
    HANM010002 = Column("HANM010002", CHAR(10), nullable=False)  # 送り状コード
    HANM010003 = Column("HANM010003", DECIMAL(8, 0), nullable=False)  # 見積個口数
    HANM010004 = Column("HANM010004", DECIMAL(8, 0), nullable=False)  # 見積才数
    HANM010005 = Column("HANM010005", DECIMAL(8, 0), nullable=False)  # 見積重量（kg）
    HANM010006 = Column("HANM010006", CHAR(8), nullable=False)  # 最安運送会社コード
    HANM010007 = Column("HANM010007", CHAR(8), nullable=False)  # 選定運送会社コード
    HANM010008 = Column("HANM010008", NVARCHAR(256), nullable=True)  # 選定理由
    
    # Timestamp columns - automatically populated on insert/update
    HAN10M010_INS = Column("HAN10M010_INS", DECIMAL(14, 6), nullable=False,
                       default=text("CONVERT([decimal](14,6),replace(replace(replace(CONVERT([nvarchar](40),getdate(),(121)),'-',''),':',''),' ',''))"))
