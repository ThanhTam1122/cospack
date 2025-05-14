from sqlalchemy.sql.expression import text
from sqlalchemy import Column, CHAR, DECIMAL, PrimaryKeyConstraint, event
from app.db.base import Base

class TransportationAreaJISMapping(Base):
    """
    運送エリア住所コード紐付マスタ (HAN99MA44UNJYUHIMODUKE)
    Transportation Area to JIS Address Code Mapping
    """
    __tablename__ = "HAN99MA44UNJYUHIMODUKE"

    # 1. 運送エリアコード - Transportation Area Code (PK)
    HANMA44001 = Column("HANMA44001", CHAR(8), nullable=False)

    # 2. JIS規格住所コード - JIS Standard Address Code (PK)
    HANMA44002 = Column("HANMA44002", CHAR(5), nullable=False)

    # 3. 更新番号 - Update Version Number, default=0, +1 on update
    HANMA44999 = Column("HANMA44999", DECIMAL(9, 0), autoincrement=True, nullable=False, default=0)

    # 4. 登録日時 - Insert timestamp
    HANMA44INS = Column("HANMA44INS", DECIMAL(20, 6), nullable=True, 
                        server_default=text("CONVERT(decimal(20,6), FORMAT(SYSDATETIME(), 'yyyyMMddHHmmss.ffffff'))"
    ))

    # 5. 更新日時 - Update timestamp
    HANMA44UPD = Column("HANMA44UPD", DECIMAL(20, 6), nullable=True, 
                        server_default=text("CONVERT(decimal(20,6), FORMAT(SYSDATETIME(), 'yyyyMMddHHmmss.ffffff'))"
    ))

    # Composite Primary Key
    __table_args__ = (
        PrimaryKeyConstraint("HANMA44001", "HANMA44002", name="pk_transportation_area_jis_mapping"),
    )

    def __repr__(self):
        return f"<TransportationAreaJISMapping area={self.HANMA44001}, jis={self.HANMA44002}>"