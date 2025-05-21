from sqlalchemy.sql.expression import text
from sqlalchemy import Column, DECIMAL, CHAR, event
from app.db.base import Base

class TransportationCapacity(Base):
    """
    運送会社キャパシティマスタ (HAN99MA47UNSOCAPA)
    Transportation Company Capacity Master
    """
    __tablename__ = "HAN99MA47UNSOCAPA"

    # 1. 運送会社コード - Carrier Code (Primary Key, CHAR(2))
    HANMA47001 = Column("HANMA47001", CHAR(2), primary_key=True, nullable=False)

    # 2. 限度才数 - Capacity Limit (DECIMAL(10,0))
    HANMA47002 = Column("HANMA47002", DECIMAL(10, 0), nullable=False)

    # 3. 最大重量（kg） - Max Weight (DECIMAL(10,0))
    HANMA47003 = Column("HANMA47003", DECIMAL(10, 0), nullable=False)

    # 4. 才数換算重量（kg） - Weight per Volume (DECIMAL(3,0))
    HANMA47004 = Column("HANMA47004", DECIMAL(3, 0), nullable=False)

    # 5. 更新番号 - Update Number (DECIMAL(9,0), starts at 0, auto +1)
    HANMA47999 = Column("HANMA47999", DECIMAL(9, 0), nullable=False, default=0)

    # 6. 登録日時 - Created Timestamp (DECIMAL(14,6))
    HANMA47INS = Column("HANMA47INS", DECIMAL(20, 6), nullable=True, 
                        server_default=text("CONVERT(decimal(20,6), FORMAT(SYSDATETIME(), 'yyyyMMddHHmmss.ffffff'))"
    ))

    # 7. 更新日時 - Updated Timestamp (DECIMAL(14,6))
    HANMA47UPD = Column("HANMA47UPD", DECIMAL(20, 6), nullable=True, 
                        server_default=text("CONVERT(decimal(20,6), FORMAT(SYSDATETIME(), 'yyyyMMddHHmmss.ffffff'))"
    ))

    def __repr__(self):
        return f"<TransportationCapacity carrier='{self.HANMA47001}'>"