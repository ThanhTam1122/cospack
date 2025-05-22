from sqlalchemy import Column, DECIMAL, CHAR
from sqlalchemy.types import NVARCHAR
from sqlalchemy.sql.expression import text
from app.db.base import Base

class CarrierSelectionLog(Base):
    """
    CosPacks選定ログ(HAN99RA42CPLOG)
    CosPacks selection log
    """
    __tablename__ = "HAN99RA42CPLOG"

    HANRA42001 = Column("HANRA42001", DECIMAL(10, 0), primary_key=True, nullable=False)  # ログ識別連番
    HANRA42002 = Column("HANRA42002", DECIMAL(10, 0), nullable=False)  # 送り状識別連番
    HANRA42003 = Column("HANRA42003", DECIMAL(8, 0), nullable=False)  # 見積個口数
    HANRA42004 = Column("HANRA42004", DECIMAL(8, 0), nullable=False)  # 見積才数
    HANRA42005 = Column("HANRA42005", DECIMAL(8, 0), nullable=False)  # 見積重量（kg）
    HANRA42006 = Column("HANRA42006", CHAR(2), nullable=False)  # 最安運送会社コード
    HANRA42007 = Column("HANRA42007", CHAR(2), nullable=False)  # 選定運送会社コード
    HANRA42008 = Column("HANRA42008", NVARCHAR(255), nullable=True)  # 選定理由
    HANRA42999 = Column("HANRA42999", DECIMAL(9, 0), nullable=False, default=0) #更新番号
    HANRA42INS = Column("HANRA42INS", DECIMAL(20, 6), nullable=True, 
                        server_default=text("CONVERT(decimal(20,6), FORMAT(SYSDATETIME(), 'yyyyMMddHHmmss.ffffff'))"
    ))
    HANRA42UPD = Column("HANRA42UPD", DECIMAL(20, 6), nullable=True, 
                        server_default=text("CONVERT(decimal(20,6), FORMAT(SYSDATETIME(), 'yyyyMMddHHmmss.ffffff'))"
    ))
    
    def __repr__(self):
        return f"<CarrierSelectionLog='{self.HANRA42001}'>"
