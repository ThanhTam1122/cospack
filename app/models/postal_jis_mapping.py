from sqlalchemy.sql.expression import text
from datetime import datetime
from sqlalchemy import Column, DECIMAL, CHAR, PrimaryKeyConstraint
from app.db.base import Base

def current_timestamp_decimal():
    now = datetime.now()
    return float(now.strftime("%Y%m%d%H%M%S") + f".{now.microsecond:06d}")

class PostalJISMapping(Base):
    """
    住所コード郵便番号紐付けマスタ(HAN99MA45JYUYUHIMODUKE)
    Postal Code to JIS Code Mapping Table
    """
    __tablename__ = "HAN99MA45JYUYUHIMODUKE"
    
    # JIS Code (JIS規格住所コード)
    HANMA45001 = Column("HANMA45001", CHAR(5), nullable=False)
    # Postal Code (郵便番号)
    HANMA45002 = Column("HANMA45002", CHAR(10), nullable=False)
    # Update Number (更新番号)
    HANMA45999 = Column("HANMA45999", DECIMAL(9, 0), nullable=False, default=0)
    # Date and time of registration  (登録日時)
    HANMA45INS = Column("HANMA45INS", DECIMAL(20, 6), nullable=True, 
                        server_default=text("CONVERT(decimal(20,6), FORMAT(SYSDATETIME(), 'yyyyMMddHHmmss.ffffff'))"
    ))
    # Update date and time (更新日時)
    HANMA45UPD = Column("HANMA45UPD", DECIMAL(20, 6), nullable=True, 
                        server_default=text("CONVERT(decimal(20,6), FORMAT(SYSDATETIME(), 'yyyyMMddHHmmss.ffffff'))"
    ))
    # Composite Primary Key
    __table_args__ = (
        PrimaryKeyConstraint('HANMA45001', 'HANMA45002', name='pk_postal_jis_mapping'),
    )

    def __repr__(self):
        return f"<PostalJISMapping {self.HANMA45002} -> {self.HANMA45001}>"