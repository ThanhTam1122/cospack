from sqlalchemy import Column, Integer, NVARCHAR
from sqlalchemy import PrimaryKeyConstraint
from app.db.base import Base

class PostalJISMapping(Base):
    """
    郵便番号JIS規格住所コード対応表 (HAN99MA45POSTALJIS)
    Postal Code to JIS Code Mapping Table
    """
    __tablename__ = "HAN99MA45POSTALJIS"
    
    # Postal Code (郵便番号)
    HANMA45001 = Column("HANMA45001", NVARCHAR(8), nullable=False)
    
    # JIS Code (JIS規格住所コード)
    HANMA45002 = Column("HANMA45002", NVARCHAR(5), nullable=False)

    # Composite Primary Key
    __table_args__ = (
        PrimaryKeyConstraint('HANMA45001', 'HANMA45002', name='pk_postal_jis_mapping'),
    )

    def __repr__(self):
        return f"<PostalJISMapping {self.HANMA45001} -> {self.HANMA45002}>"