from sqlalchemy.sql.expression import text
from sqlalchemy import Column, DECIMAL, event
from sqlalchemy.dialects.mssql import NVARCHAR, CHAR
from app.db.base import Base

class TransportationArea(Base):
    """
    運送エリアマスタ (HAN99MA43UNSOAREA)
    Transportation Area Master
    """
    __tablename__ = "HAN99MA43UNSOAREA"

    # 1. 運送エリアコード - Transportation Area Code (Primary Key)
    HANMA43001 = Column("HANMA43001", CHAR(8), primary_key=True, nullable=False)

    # 2. 運送エリア名 - Area Name
    HANMA43002 = Column("HANMA43002", NVARCHAR(255), nullable=True)

    # 3. 距離（km） - Distance in KM
    HANMA43003 = Column("HANMA43003", DECIMAL(5, 0), nullable=False, default=0)

    # 4. 更新番号 - Update Version Number, default 0 on insert, +1 on update
    HANMA43999 = Column("HANMA43999", DECIMAL(9, 0), autoincrement=True, nullable=False, default=0)

    # 5. 登録日時 - Insert Timestamp (yyyymmddhhmiss.ffffff)
    HANMA43INS = Column("HANMA43INS", DECIMAL(20, 6), nullable=True, 
                        server_default=text("CONVERT(decimal(20,6), FORMAT(SYSDATETIME(), 'yyyyMMddHHmmss.ffffff'))"
    ))

    # 6. 更新日時 - Update Timestamp (yyyymmddhhmiss.ffffff)
    HANMA43UPD = Column("HANMA43UPD", DECIMAL(20, 6), nullable=True, 
                        server_default=text("CONVERT(decimal(20,6), FORMAT(SYSDATETIME(), 'yyyyMMddHHmmss.ffffff'))"
    ))

    def __repr__(self):
        return f"<TransportationArea code={self.HANMA43001}, name={self.HANMA43002}>"