from sqlalchemy.sql.expression import text
from sqlalchemy import Column, DECIMAL, CHAR, NVARCHAR
from app.db.base import Base

class Waybill(Base):
    """
    CosPacks送り状(HAN99RA41CPOKURIJYO)
    Waybill Master
    """
    __tablename__ = "HAN99RA41CPOKURIJYO"

    HANRA41001 = Column("HANRA41001", DECIMAL(10, 0), primary_key=True,  nullable=False)  # 送り状識別連番
    HANRA41002 = Column("HANRA41002", DECIMAL(8, 0), nullable=True)  # 出荷予定日
    HANRA41003 = Column("HANRA41003", DECIMAL(8, 0), nullable=True)  # 納期日
    HANRA41004 = Column("HANRA41004", CHAR(11), nullable=True)  # 取引先コード
    HANRA41005 = Column("HANRA41005", DECIMAL(1, 0), nullable=True)  # 納期情報1
    HANRA41006 = Column("HANRA41006", DECIMAL(1, 0), nullable=True) # 納期情報2
    HANRA41007 = Column("HANRA41007", NVARCHAR(32), nullable=True) # 納品先名1
    HANRA41008 = Column("HANRA41008", NVARCHAR(32), nullable=True) # 納品先名2
    HANRA41009 = Column("HANRA41009", CHAR(10), nullable=True)  # 納品先郵便番号
    HANRA41010 = Column("HANRA41010", NVARCHAR(32), nullable=True)  # 納品先住所1
    HANRA41011 = Column("HANRA41011", NVARCHAR(32), nullable=True)  # 納品先住所2
    HANRA41012 = Column("HANRA41012", NVARCHAR(32), nullable=True)  # 納品先住所3
    HANRA41999 = Column("HANRA41999", DECIMAL(9, 0), nullable=False, default=0) #更新番号
    HANRA41INS = Column("HANRA41INS", DECIMAL(20, 6), nullable=True, 
                        server_default=text("CONVERT(decimal(20,6), FORMAT(SYSDATETIME(), 'yyyyMMddHHmmss.ffffff'))"
    )) #登録日時
    HANRA41UPD = Column("HANRA41UPD", DECIMAL(20, 6), nullable=True, 
                        server_default=text("CONVERT(decimal(20,6), FORMAT(SYSDATETIME(), 'yyyyMMddHHmmss.ffffff'))"
    )) #更新日時
    def __repr__(self):
        return f"<Waybill='{self.HANRA41001}'>"
