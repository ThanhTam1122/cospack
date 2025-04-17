from sqlalchemy import Column, Integer, String, Date, Boolean, Float
from sqlalchemy.types import DECIMAL
from sqlalchemy.dialects.mssql import NVARCHAR, CHAR, VARCHAR
from sqlalchemy.sql.expression import text
from app.db.base import Base

class TransportationCompanySubMaster(Base):
    """
    運送会社サブマスター (HAN99MA03UNSOU_SUB)
    Transportation Company Sub Master
    """
    __tablename__ = "HAN99MA03UNSOU_SUB"
    
    # Composite primary key fields
    HANMA03001 = Column("HANMA03001", CHAR(2), primary_key=True, nullable=False, default='')  # 運送会社コード
    HANMA03002 = Column("HANMA03002", DECIMAL(1, 0), primary_key=True, nullable=False, default=0)  # 出荷場所
    HANMA03003 = Column("HANMA03003", CHAR(2), primary_key=True, nullable=False, default='')  # 都道府県コード
    
    # Data fields
    HANMA03004 = Column("HANMA03004", DECIMAL(2, 0), nullable=False, default=0)  # 出荷リードタイム
    
    # Transportation fee fields
    HANMA03005 = Column("HANMA03005", DECIMAL(15, 4), nullable=False, default=0)  # 運送費単価１
    HANMA03006 = Column("HANMA03006", DECIMAL(15, 4), nullable=False, default=0)  # 運送費単価２
    HANMA03007 = Column("HANMA03007", DECIMAL(15, 4), nullable=False, default=0)  # 運送費単価３
    HANMA03008 = Column("HANMA03008", DECIMAL(15, 4), nullable=False, default=0)  # 運送費単価４
    HANMA03009 = Column("HANMA03009", DECIMAL(15, 4), nullable=False, default=0)  # 運送費単価５
    HANMA03010 = Column("HANMA03010", DECIMAL(15, 4), nullable=False, default=0)  # 運送費単価６
    HANMA03011 = Column("HANMA03011", DECIMAL(15, 4), nullable=False, default=0)  # 運送費単価７
    HANMA03012 = Column("HANMA03012", DECIMAL(15, 4), nullable=False, default=0)  # 運送費単価８
    HANMA03013 = Column("HANMA03013", DECIMAL(15, 4), nullable=False, default=0)  # 運送費単価９
    HANMA03014 = Column("HANMA03014", DECIMAL(15, 4), nullable=False, default=0)  # 運送費単価１０
    HANMA03015 = Column("HANMA03015", DECIMAL(15, 4), nullable=False, default=0)  # 運送費単価１１
    
    # System fields
    HANMA03999 = Column("HANMA03999", DECIMAL(9, 0), nullable=False, default=0)  # 更新番号
    
    def __repr__(self):
        return f"<TransportationCompanySubMaster {self.HANMA03001}-{self.HANMA03002}-{self.HANMA03003}>" 