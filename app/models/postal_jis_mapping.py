from sqlalchemy import Column, Integer
from sqlalchemy.dialects.mssql import NVARCHAR
from app.db.base import Base

class PostalJISMapping(Base):
    """
    郵便番号JIS規格住所コード対応表 (HAN99MA45POSTALJIS)
    Postal Code to JIS Code Mapping Table
    """
    __tablename__ = "HAN99MA45POSTALJIS"
    
    HANMA45001 = Column("HANMA45001", NVARCHAR(8), nullable=False)  # PostalCode (郵便番号)
    HANMA45002 = Column("HANMA45002", NVARCHAR(5), nullable=False)  # JISCode (JIS規格住所コード)

    ID = Column("ID", Integer, nullable=False, primary_key=True)

    def __repr__(self):
        return f"<PostalJISMapping {self.HANMA45002} -> {self.HANMA45003}>" 