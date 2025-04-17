from sqlalchemy import Column, Integer, String, Date, Boolean, Float
from sqlalchemy.types import DECIMAL
from sqlalchemy.dialects.mssql import NVARCHAR, CHAR, VARCHAR
from sqlalchemy.sql.expression import text
from app.db.base import Base

class HolidayCalendarMaster(Base):
    """
    休日カレンダーマスター (HAN99MA04CALENDAR1)
    Holiday Calendar Master
    """
    __tablename__ = "HAN99MA04CALENDAR1"
    
    # Composite primary key fields
    HANMA04001 = Column("HANMA04001", CHAR(2), primary_key=True, nullable=False, default='')  # 会社コード
    HANMA04002 = Column("HANMA04002", DECIMAL(8, 0), primary_key=True, nullable=False, default=0)  # 休日(年月日)
    
    # Data fields
    HANMA04003 = Column("HANMA04003", DECIMAL(1, 0), nullable=False, default=0)  # 配送区分
    
    # System fields
    HANMA04999 = Column("HANMA04999", DECIMAL(9, 0), nullable=False, default=0)  # 更新番号
    
    def __repr__(self):
        return f"<HolidayCalendarMaster {self.HANMA04001}-{self.HANMA04002}>" 