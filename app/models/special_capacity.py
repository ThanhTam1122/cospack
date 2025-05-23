from sqlalchemy.sql.expression import text
from sqlalchemy import Column, DECIMAL, CHAR, PrimaryKeyConstraint
from app.db.base import Base
from datetime import datetime

class SpecialCapacity(Base):
    """
    運送会社特殊キャパシティマスタ (HAN99MA48UNSOTOKUCAPA)
    Transportation company special capacity master
    """
    __tablename__ = "HAN99MA48UNSOTOKUCAPA"

    # 1. 運送会社コード - Carrier Code (Primary Key, CHAR(2))
    HANMA48001 = Column("HANMA48001", CHAR(2), nullable=False)

    # 2. 限度才数 - Capacity Limit (DECIMAL(10,0))
    HANMA48002 = Column("HANMA48002", DECIMAL(8, 0), nullable=False)

    # 3. 最大重量（kg） - Max Weight (DECIMAL(10,0))
    HANMA48003 = Column("HANMA48003", DECIMAL(10, 0), nullable=False)

    # 4. 才数換算重量（kg） - Weight per Volume (DECIMAL(3,0))
    HANMA48004 = Column("HANMA48004", DECIMAL(10, 0), nullable=False)

    # 5. 更新番号 - Update Number (DECIMAL(9,0))
    HANMA48999 = Column("HANMA48999", DECIMAL(9, 0), nullable=False, default=0)

    # 6. 登録日時 - Created Timestamp (DECIMAL(14,6))
    HANMA48INS = Column("HANMA48INS", DECIMAL(20, 6), nullable=True, 
                        server_default=text("CONVERT(decimal(20,6), FORMAT(SYSDATETIME(), 'yyyyMMddHHmmss.ffffff'))"
    ))

    # 7. 更新日時 - Updated Timestamp (DECIMAL(14,6))
    HANMA48UPD = Column("HANMA48UPD", DECIMAL(20, 6), nullable=True, 
                        server_default=text("CONVERT(decimal(20,6), FORMAT(SYSDATETIME(), 'yyyyMMddHHmmss.ffffff'))"
    ))

    # Composite Primary Key
    __table_args__ = (
        PrimaryKeyConstraint('HANMA48001', 'HANMA48002', name='pk_special_capacity'),
    )

    def __repr__(self):
        return f"<SpecialCapacity carrier='{self.HANMA48001}'>"