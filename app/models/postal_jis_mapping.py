from sqlalchemy import Column, Integer, String, Date, Boolean, Float
from sqlalchemy.types import DECIMAL
from sqlalchemy.dialects.mssql import NVARCHAR, CHAR, VARCHAR
from sqlalchemy.sql.expression import text
from app.db.base import Base

class PostalJISMapping(Base):
    """
    郵便番号JIS規格住所コード対応表 (HAN99MA45POSTALJIS)
    Postal Code to JIS Code Mapping Table
    """
    __tablename__ = "HAN99MA45POSTALJIS"
    
    # Primary key
    HANMA45001 = Column("HANMA45001", Integer, primary_key=True, nullable=False)  # ID
    
    # Data fields
    HANMA45002 = Column("HANMA45002", NVARCHAR(8), nullable=False)  # PostalCode (郵便番号)
    HANMA45003 = Column("HANMA45003", NVARCHAR(5), nullable=False)  # JISCode (JIS規格住所コード)
    HANMA45004 = Column("HANMA45004", NVARCHAR(100))  # PrefectureName (都道府県名)
    HANMA45005 = Column("HANMA45005", NVARCHAR(100))  # CityName (市区町村名)
    HANMA45006 = Column("HANMA45006", NVARCHAR(200))  # StreetName (町域名)
    
    # System fields
    HANMA45INS = Column("HANMA45INS", DECIMAL(14, 6), nullable=False, 
                       default=text("CONVERT([decimal](14,6),replace(replace(replace(CONVERT([nvarchar](40),getdate(),(121)),'-',''),':',''),' ',''))"))  # 登録日時
    HANMA45UPD = Column("HANMA45UPD", DECIMAL(14, 6), nullable=False,
                       default=text("CONVERT([decimal](14,6),replace(replace(replace(CONVERT([nvarchar](40),getdate(),(121)),'-',''),':',''),' ',''))"))  # 更新日時
    HANMA45999 = Column("HANMA45999", DECIMAL(9, 0), nullable=False, default=0)  # 更新番号
    
    def __repr__(self):
        return f"<PostalJISMapping {self.HANMA45002} -> {self.HANMA45003}>" 