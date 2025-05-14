from sqlalchemy.sql.expression import text
from sqlalchemy import Column, DECIMAL, CHAR, event, PrimaryKeyConstraint
from sqlalchemy.types import BigInteger
from app.db.base import Base

class CarrierSelectionLogDetail(Base):
    """
    CosPacks選定ログ詳細(HAN99RA43CPLOGDETAIL)
    CosPacks selection log details
    """
    __tablename__ = "HAN99RA43CPLOGDETAIL"

    # ログ識別連番 - Log Code
    HANRA43001 = Column("HANRA43001", CHAR(10), nullable=False)
    # 商品コード - Product Code
    HANRA43002 = Column("HANRA43002", CHAR(8), nullable=False)
    # 見積サイズ（cm） - Estimated Size (cm)
    HANRA43003 = Column("HANRA43003", DECIMAL(8, 0), nullable=False)
    # 見積個口数 - Estimated Parcel Count
    HANRA43004 = Column("HANRA43004", DECIMAL(5, 0), nullable=False)
    # 更新番号 - Update Number
    HANRA43999 = Column("HANRA43999", DECIMAL(9, 0), autoincrement=True, nullable=False, default=0)
    # 登録日時 - Date and time of registration
    HANRA43INS = Column("HANRA43INS", DECIMAL(20, 6), nullable=True, 
                        server_default=text("CONVERT(decimal(20,6), FORMAT(SYSDATETIME(), 'yyyyMMddHHmmss.ffffff'))"
    ))
    # 更新日時 - Update date and time
    HANRA43UPD = Column("HANRA43UPD", DECIMAL(20, 6), nullable=True, 
                        server_default=text("CONVERT(decimal(20,6), FORMAT(SYSDATETIME(), 'yyyyMMddHHmmss.ffffff'))"
    ))
    # Composite Primary Key
    __table_args__ = (
        PrimaryKeyConstraint('HANRA43001', 'HANRA43002', name='pk_carrier_selection_log_detail'),
    )
