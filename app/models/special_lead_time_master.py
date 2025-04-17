from sqlalchemy import Column, Integer, String, Date, Boolean, Float
from sqlalchemy.types import DECIMAL
from sqlalchemy.dialects.mssql import NVARCHAR, CHAR, VARCHAR
from sqlalchemy.sql.expression import text
from app.db.base import Base

class SpecialLeadTimeMaster(Base):
    """
    特殊リードタイムマスター (HAN99MA41TOKULEADTIME)
    Special Lead Time Master
    """
    __tablename__ = "HAN99MA41TOKULEADTIME"
    
    # Composite primary key fields
    HANMA41001 = Column("HANMA41001", CHAR(2), primary_key=True, nullable=False, default='')  # 運送会社コード
    HANMA41002 = Column("HANMA41002", CHAR(2), primary_key=True, nullable=False, default='')  # 都道府県コード
    HANMA41003 = Column("HANMA41003", DECIMAL(8, 0), primary_key=True, nullable=False, default=0)  # 出荷予定日
    
    # Data fields
    HANMA41004 = Column("HANMA41004", DECIMAL(8, 0), nullable=False, default=0)  # 納期日
    
    # System fields
    HANMA41INS = Column("HANMA41INS", DECIMAL(14, 6), nullable=False,
                       default=text("CONVERT([decimal](14,6),replace(replace(replace(CONVERT([nvarchar](40),getdate(),(121)),'-',''),':',''),' ',''))"))  # 登録日時
    HANMA41UPD = Column("HANMA41UPD", DECIMAL(14, 6), nullable=False,
                       default=text("CONVERT([decimal](14,6),replace(replace(replace(CONVERT([nvarchar](40),getdate(),(121)),'-',''),':',''),' ',''))"))  # 更新日時
    HANMA41999 = Column("HANMA41999", DECIMAL(9, 0), nullable=False, default=0)  # 更新番号
    
    def __repr__(self):
        return f"<SpecialLeadTimeMaster {self.HANMA41001}-{self.HANMA41002}-{self.HANMA41003}>" 