from sqlalchemy.sql.expression import text
from sqlalchemy import Column, DECIMAL, CHAR, event
from app.db.base import Base


class TransportationFee(Base):
    """
    運送料金マスタ (HAN99MA46SORYO)
    Transportation Fee Master
    """
    __tablename__ = "HAN99MA46SORYO"

    # 1. 運送料金コード - Transportation Fee Code (Primary Key)
    HANMA46001 = Column("HANMA46001", CHAR(10), primary_key=True, nullable=False)

    # 2. 運送会社コード - Transport Company Code
    HANMA46002 = Column("HANMA46002", CHAR(2), nullable=False)

    # 3. 運送エリアコード - Transport Area Code
    HANMA46003 = Column("HANMA46003", CHAR(8), nullable=False)

    # 4. 最大重量（kg） - Max Weight (default 0, NOT NULL)
    HANMA46004 = Column("HANMA46004", DECIMAL(5, 0), nullable=False, default=0, server_default=text("CONVERT(decimal(5,0), 0)"))

    # 5. 最大才数 - Max Volume (default 0, NOT NULL)
    HANMA46005 = Column("HANMA46005", DECIMAL(5, 0), nullable=False, default=0, server_default=text("CONVERT(decimal(5,0), 0)"))

    # 6. 最大サイズ（cm） - Max Dimensions (default 0, NOT NULL)
    HANMA46006 = Column("HANMA46006", DECIMAL(5, 0), nullable=False, default=0, server_default=text("CONVERT(decimal(5,0), 0)"))

    # 7. 才数単価 - Price per Unit Volume (default 0, NOT NULL)
    HANMA46007 = Column("HANMA46007", DECIMAL(14, 0), nullable=False, default=0, server_default=text("CONVERT(decimal(5,0), 0)"))

    # 8. マイナス才数 - Minus Volume (default 0, NOT NULL)
    HANMA46008 = Column("HANMA46008", DECIMAL(5, 0), nullable=False, default=0, server_default=text("CONVERT(decimal(5,0), 0)"))

    # 9. 基準額 - Base Price (nullable OK)
    HANMA46009 = Column("HANMA46009", DECIMAL(14, 0), nullable=False)

    # 10. 料金タイプ - Fee Type (1=fixed, 2=per unit, 3=per item)
    HANMA46010 = Column("HANMA46010", DECIMAL(1, 0), nullable=False)

    # 11. 更新番号 - Update Version Number (default 0, +1 on update)
    HANMA46999 = Column("HANMA46999", DECIMAL(9, 0), nullable=False, default=0)

    # 12. 登録日時 - Created Timestamp (DECIMAL(14,6))
    HANMA46INS = Column("HANMA46INS",DECIMAL(20, 6), nullable=True, 
                        server_default=text("CONVERT(decimal(20,6), FORMAT(SYSDATETIME(), 'yyyyMMddHHmmss.ffffff'))"
    ))
    # 13. 更新日時 - Update Timestamp (DECIMAL(14,6))
    HANMA46UPD = Column("HANMA46UPD", DECIMAL(20, 6), nullable=True, 
                        server_default=text("CONVERT(decimal(20,6), FORMAT(SYSDATETIME(), 'yyyyMMddHHmmss.ffffff'))"
    ))

    def __repr__(self):
        return f"<TransportationFee code='{self.HANMA46001}'>"