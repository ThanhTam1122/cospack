from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Numeric, CHAR, Text
from sqlalchemy.types import DECIMAL
from sqlalchemy.dialects.mssql import NVARCHAR, DATETIME2, MONEY, UNIQUEIDENTIFIER, VARCHAR, SMALLDATETIME, BIT
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import text
from app.db.base import Base
import uuid

class FujiTradingPickingManagement(Base):
    """
    Represents the HAN99CA11PICKING table for Fuji Trading Picking Management
    """
    __tablename__ = "HAN99CA11PICKING"
    
    # Primary key and identification columns
    HANCA11001 = Column("HANCA11001", DECIMAL, primary_key=True, nullable=False, default=0)
    HANCA11002 = Column("HANCA11002", DECIMAL, nullable=False, default=0)
    HANCA11999 = Column("HANCA11999", DECIMAL, nullable=False, default=0)
    
    # Timestamp columns - automatically populated on insert/update
    HANCA11INS = Column("HANCA11INS", DECIMAL(20, 6), nullable=False, 
                       default=text("CONVERT([decimal](20,6),replace(replace(replace(CONVERT([nvarchar](40),getdate(),(121)),'-',''),':',''),' ',''))"))
    HANCA11UPD = Column("HANCA11UPD", DECIMAL(20, 6), nullable=False,
                       default=text("CONVERT([decimal](20,6),replace(replace(replace(CONVERT([nvarchar](40),getdate(),(121)),'-',''),':',''),' ',''))"))
    
    # Relationships
    picking_details = relationship("PickingDetail", back_populates="picking_header", cascade="all, delete-orphan")
    picking_works = relationship("PickingWork", back_populates="picking_header", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<HAN99CA11PICKING {self.HANCA11001}>"


class PickingDetail(Base):
    """
    Represents the HAN10C016PICKING table for Picking Details
    """
    __tablename__ = "HAN10C016PICKING"
    
    # Primary key and identification columns
    HANC016001 = Column("HANC016001", DECIMAL, primary_key=True, nullable=False, default=0)
    HANC016002 = Column("HANC016002", DECIMAL, nullable=False, default=0)
    HANC016003 = Column("HANC016003", DECIMAL, nullable=False, default=0)
    HANC016004 = Column("HANC016004", DECIMAL, nullable=False, default=0)
    HANC016005 = Column("HANC016005", DECIMAL, nullable=False, default=0)
    HANC016006 = Column("HANC016006", DECIMAL, nullable=False, default=0)
    
    # String data columns
    HANC016007 = Column("HANC016007", CHAR(11), nullable=False, default='')
    HANC016008 = Column("HANC016008", CHAR(11), nullable=False, default='')
    HANC016009 = Column("HANC016009", CHAR(8), nullable=False, default='')
    HANC016010 = Column("HANC016010", CHAR(8), nullable=False, default='')
    HANC016011 = Column("HANC016011", CHAR(4), nullable=False, default='')
    HANC016012 = Column("HANC016012", CHAR(4), nullable=False, default='')
    
    # Numeric data columns
    HANC016013 = Column("HANC016013", DECIMAL, nullable=False, default=0)
    HANC016014 = Column("HANC016014", DECIMAL, nullable=False, default=0)
    HANC016015 = Column("HANC016015", DECIMAL, nullable=False, default=0)
    HANC016016 = Column("HANC016016", DECIMAL, nullable=False, default=0)
    HANC016017 = Column("HANC016017", DECIMAL, nullable=False, default=0)
    HANC016018 = Column("HANC016018", DECIMAL, nullable=False, default=0)
    
    # Additional string fields
    HANC016019 = Column("HANC016019", CHAR(4), nullable=False, default='')
    HANC016020 = Column("HANC016020", CHAR(25), nullable=False, default='')
    HANC016021 = Column("HANC016021", CHAR(25), nullable=False, default='')
    HANC016022 = Column("HANC016022", CHAR(25), nullable=False, default='')
    HANC016023 = Column("HANC016023", CHAR(25), nullable=False, default='')
    
    # More numeric fields
    HANC016024 = Column("HANC016024", DECIMAL, nullable=False, default=0)
    HANC016025 = Column("HANC016025", DECIMAL, nullable=False, default=0)
    
    # Additional fields for relationships
    HANC016A001 = Column("HANC016A001", DECIMAL, nullable=False, default=0)
    HANC016A002 = Column("HANC016A002", DECIMAL, nullable=False, default=0)
    HANC016A003 = Column("HANC016A003", CHAR(11), nullable=False, default='')
    HANC016A004 = Column("HANC016A004", CHAR(11), nullable=False, default='')
    HANC016A005 = Column("HANC016A005", DECIMAL, nullable=False, default=0)
    HANC016A006 = Column("HANC016A006", DECIMAL, nullable=False, default=0)
    HANC016A007 = Column("HANC016A007", DECIMAL, nullable=False, default=0)
    HANC016A008 = Column("HANC016A008", DECIMAL, nullable=False, default=0)
    
    # Tracking and system fields
    HANC016999 = Column("HANC016999", DECIMAL, nullable=False, default=0)
    HANC016INS = Column("HANC016INS", DECIMAL(20, 6), nullable=False, 
                       default=text("CONVERT([decimal](20,6),replace(replace(replace(CONVERT([nvarchar](40),getdate(),(121)),'-',''),':',''),' ',''))"))
    HANC016UPD = Column("HANC016UPD", DECIMAL(20, 6), nullable=False,
                       default=text("CONVERT([decimal](20,6),replace(replace(replace(CONVERT([nvarchar](40),getdate(),(121)),'-',''),':',''),' ',''))"))
    
    # Relationship to header
    picking_header = relationship("FujiTradingPickingManagement", back_populates="picking_details")

    def __repr__(self):
        return f"<HAN10C016PICKING {self.HANC016001}>"


class PickingWork(Base):
    """
    Represents the HAN10W002PICKINGW table for Picking Work
    """
    __tablename__ = "HAN10W002PICKINGW"
    
    # Primary key columns
    HANW002001 = Column("HANW002001", DECIMAL, primary_key=True, nullable=False, default=0)
    HANW002002 = Column("HANW002002", DECIMAL, primary_key=True, nullable=False, default=0)
    HANW002003 = Column("HANW002003", DECIMAL, primary_key=True, nullable=False, default=0)
    HANW002078 = Column("HANW002078", DECIMAL, primary_key=True, nullable=False, default=0)
    
    # Core numeric columns
    HANW002004 = Column("HANW002004", DECIMAL, nullable=False, default=0)
    HANW002005 = Column("HANW002005", DECIMAL, nullable=False, default=0)
    HANW002006 = Column("HANW002006", DECIMAL, nullable=False, default=0)
    HANW002007 = Column("HANW002007", DECIMAL, nullable=False, default=0)
    HANW002008 = Column("HANW002008", DECIMAL, nullable=False, default=0)
    HANW002009 = Column("HANW002009", DECIMAL, nullable=False, default=0)
    HANW002010 = Column("HANW002010", DECIMAL, nullable=False, default=0)
    HANW002011 = Column("HANW002011", DECIMAL, nullable=False, default=0)
    HANW002012 = Column("HANW002012", DECIMAL, nullable=False, default=0)
    
    # String based columns
    HANW002013 = Column("HANW002013", CHAR(11), nullable=False, default='')
    HANW002014 = Column("HANW002014", CHAR(8), nullable=False, default='')
    HANW002015 = Column("HANW002015", CHAR(8), nullable=False, default='')
    HANW002016 = Column("HANW002016", CHAR(6), nullable=False, default='')
    
    # More numeric columns
    HANW002017 = Column("HANW002017", DECIMAL, nullable=False, default=0)
    HANW002018 = Column("HANW002018", DECIMAL, nullable=False, default=0)
    HANW002019 = Column("HANW002019", DECIMAL, nullable=False, default=0)
    HANW002020 = Column("HANW002020", DECIMAL, nullable=False, default=0)
    
    # More string columns
    HANW002021 = Column("HANW002021", CHAR(11), nullable=False, default='')
    HANW002022 = Column("HANW002022", CHAR(20), nullable=False, default='')
    HANW002023 = Column("HANW002023", CHAR(4), nullable=False, default='')
    HANW002024 = Column("HANW002024", CHAR(10), nullable=False, default='')
    HANW002025 = Column("HANW002025", CHAR(5), nullable=False, default='')
    
    # Nullable varchar columns
    HANW002026 = Column("HANW002026", NVARCHAR(36), nullable=True)
    HANW002027 = Column("HANW002027", NVARCHAR(48), nullable=True)
    HANW002028 = Column("HANW002028", NVARCHAR(48), nullable=True)
    HANW002029 = Column("HANW002029", NVARCHAR(48), nullable=True)
    
    # More string columns
    HANW002030 = Column("HANW002030", CHAR(25), nullable=False, default='')
    HANW002031 = Column("HANW002031", CHAR(20), nullable=False, default='')
    HANW002032 = Column("HANW002032", CHAR(20), nullable=False, default='')
    HANW002033 = Column("HANW002033", CHAR(20), nullable=False, default='')
    
    # More nullable varchar columns
    HANW002034 = Column("HANW002034", NVARCHAR(36), nullable=True)
    HANW002035 = Column("HANW002035", NVARCHAR(4), nullable=True)
    
    # Decimal columns with precision
    HANW002036 = Column("HANW002036", DECIMAL(19, 4), nullable=False, default=0)
    HANW002037 = Column("HANW002037", DECIMAL(19, 4), nullable=False, default=0)
    
    # More nullable varchar
    HANW002038 = Column("HANW002038", NVARCHAR(4), nullable=True)
    
    # More decimal columns with precision
    HANW002039 = Column("HANW002039", DECIMAL(19, 4), nullable=False, default=0)
    HANW002040 = Column("HANW002040", DECIMAL(19, 4), nullable=False, default=0)
    HANW002041 = Column("HANW002041", DECIMAL(19, 4), nullable=False, default=0)
    HANW002042 = Column("HANW002042", DECIMAL(19, 4), nullable=False, default=0)
    HANW002043 = Column("HANW002043", DECIMAL(19, 4), nullable=False, default=0)
    HANW002044 = Column("HANW002044", DECIMAL(19, 4), nullable=False, default=0)
    HANW002045 = Column("HANW002045", DECIMAL(19, 4), nullable=False, default=0)
    
    # Regular decimal columns
    HANW002046 = Column("HANW002046", DECIMAL, nullable=False, default=0)
    
    # Special precision decimals
    HANW002047 = Column("HANW002047", DECIMAL(4, 1), nullable=False, default=0)
    HANW002048 = Column("HANW002048", DECIMAL(19, 4), nullable=False, default=0)
    HANW002049 = Column("HANW002049", DECIMAL(19, 4), nullable=False, default=0)
    HANW002050 = Column("HANW002050", DECIMAL(19, 4), nullable=False, default=0)
    
    # Regular decimal
    HANW002051 = Column("HANW002051", DECIMAL, nullable=False, default=0)
    
    # Special precision decimal
    HANW002052 = Column("HANW002052", DECIMAL(4, 2), nullable=False, default=0)
    HANW002053 = Column("HANW002053", DECIMAL(19, 4), nullable=False, default=0)
    
    # Regular decimal
    HANW002054 = Column("HANW002054", DECIMAL, nullable=False, default=0)
    
    # String column
    HANW002055 = Column("HANW002055", CHAR(5), nullable=False, default='')
    
    # Nullable strings
    HANW002056 = Column("HANW002056", NVARCHAR(12), nullable=True)
    HANW002057 = Column("HANW002057", NVARCHAR(12), nullable=True)
    
    # String and decimal columns
    HANW002058 = Column("HANW002058", CHAR(3), nullable=False, default='')
    HANW002059 = Column("HANW002059", DECIMAL, nullable=False, default=0)
    HANW002060 = Column("HANW002060", DECIMAL, nullable=False, default=0)
    
    # Decimal columns with precision
    HANW002061 = Column("HANW002061", DECIMAL(19, 4), nullable=False, default=0)
    HANW002062 = Column("HANW002062", DECIMAL(19, 4), nullable=False, default=0)
    HANW002063 = Column("HANW002063", DECIMAL(19, 4), nullable=False, default=0)
    
    # Regular decimal columns
    HANW002064 = Column("HANW002064", DECIMAL, nullable=False, default=0)
    HANW002065 = Column("HANW002065", DECIMAL, nullable=False, default=0)
    
    # String column
    HANW002066 = Column("HANW002066", CHAR(8), nullable=False, default='')
    
    # Regular decimal column
    HANW002067 = Column("HANW002067", DECIMAL, nullable=False, default=0)
    
    # Decimal with precision
    HANW002068 = Column("HANW002068", DECIMAL(19, 4), nullable=False, default=0)
    
    # String column
    HANW002069 = Column("HANW002069", CHAR(4), nullable=False, default='')
    
    # Regular decimal column
    HANW002070 = Column("HANW002070", DECIMAL, nullable=False, default=0)
    
    # System tracking field
    HANW002999 = Column("HANW002999", DECIMAL, nullable=False, default=0)
    
    # String columns
    HANW002071 = Column("HANW002071", CHAR(20), nullable=False, default='')
    HANW002072 = Column("HANW002072", CHAR(2), nullable=False, default='')
    HANW002073 = Column("HANW002073", CHAR(8), nullable=False, default='')
    
    # Regular decimal columns
    HANW002914 = Column("HANW002914", DECIMAL, nullable=False, default=0)
    HANW002915 = Column("HANW002915", DECIMAL, nullable=False, default=0)
    
    # Nullable strings
    HANW002916 = Column("HANW002916", NVARCHAR(64), nullable=True)
    
    # String column
    HANW002917 = Column("HANW002917", CHAR(32), nullable=False, default='')
    
    # Regular decimal column
    HANW002918 = Column("HANW002918", DECIMAL, nullable=False, default=0)
    
    # Nullable string
    HANW002919 = Column("HANW002919", NVARCHAR(64), nullable=True)
    
    # Decimal with precision
    HANW002074 = Column("HANW002074", DECIMAL(19, 4), nullable=False, default=0)
    
    # Regular decimal columns
    HANW002075 = Column("HANW002075", DECIMAL, nullable=False, default=0)
    HANW002076 = Column("HANW002076", DECIMAL, nullable=False, default=0)
    
    # String column
    HANW002077 = Column("HANW002077", CHAR(20), nullable=False, default='')
    
    # Regular decimal columns (HANW002078 is already defined as primary key)
    HANW002079 = Column("HANW002079", DECIMAL, nullable=False, default=0)
    HANW002080 = Column("HANW002080", DECIMAL, nullable=False, default=0)
    
    # Timestamp columns - automatically populated
    HANW002INS = Column("HANW002INS", DECIMAL(20, 6), nullable=False, 
                       default=text("CONVERT([decimal](20,6),replace(replace(replace(CONVERT([nvarchar](40),getdate(),(121)),'-',''),':',''),' ',''))"))
    HANW002UPD = Column("HANW002UPD", DECIMAL(20, 6), nullable=False,
                       default=text("CONVERT([decimal](20,6),replace(replace(replace(CONVERT([nvarchar](40),getdate(),(121)),'-',''),':',''),' ',''))"))
    
    # Regular decimal columns
    HANW002081 = Column("HANW002081", DECIMAL, nullable=False, default=0)
    
    # String column
    HANW002082 = Column("HANW002082", CHAR(4), nullable=False, default='')
    
    # Regular decimal columns
    HANW002083 = Column("HANW002083", DECIMAL, nullable=False, default=0)
    HANW002084 = Column("HANW002084", DECIMAL, nullable=False, default=0)
    
    # String columns
    HANW002085 = Column("HANW002085", CHAR(11), nullable=False, default='')
    HANW002086 = Column("HANW002086", CHAR(10), nullable=False, default='')
    HANW002087 = Column("HANW002087", CHAR(20), nullable=False, default='')
    
    # Regular decimal column
    HANW002088 = Column("HANW002088", DECIMAL, nullable=False, default=0)
    
    # String columns
    HANW002089 = Column("HANW002089", CHAR(4), nullable=False, default='')
    HANW002090 = Column("HANW002090", CHAR(25), nullable=False, default='')
    HANW002091 = Column("HANW002091", CHAR(25), nullable=False, default='')
    
    # Additional decimal columns - just listing some of them
    HANW002092 = Column("HANW002092", DECIMAL, nullable=False, default=0)
    HANW002093 = Column("HANW002093", DECIMAL, nullable=False, default=0)
    HANW002094 = Column("HANW002094", DECIMAL, nullable=False, default=0)
    HANW002095 = Column("HANW002095", DECIMAL, nullable=False, default=0)
    HANW002096 = Column("HANW002096", DECIMAL, nullable=False, default=0)
    HANW002097 = Column("HANW002097", DECIMAL, nullable=False, default=0)
    HANW002098 = Column("HANW002098", DECIMAL, nullable=False, default=0)
    HANW002099 = Column("HANW002099", DECIMAL, nullable=False, default=0)
    HANW002100 = Column("HANW002100", DECIMAL, nullable=False, default=0)
    HANW002101 = Column("HANW002101", DECIMAL, nullable=False, default=0)
    HANW002102 = Column("HANW002102", DECIMAL, nullable=False, default=0)
    HANW002103 = Column("HANW002103", DECIMAL, nullable=False, default=0)
    HANW002104 = Column("HANW002104", DECIMAL, nullable=False, default=0)
    HANW002105 = Column("HANW002105", DECIMAL, nullable=False, default=0)
    HANW002106 = Column("HANW002106", DECIMAL, nullable=False, default=0)
    HANW002107 = Column("HANW002107", DECIMAL, nullable=False, default=0)
    HANW002108 = Column("HANW002108", DECIMAL, nullable=False, default=0)
    HANW002109 = Column("HANW002109", DECIMAL, nullable=False, default=0)
    
    # A few more of the decimal columns - not listing all for brevity
    HANW002110 = Column("HANW002110", DECIMAL(9, 4), nullable=False, default=0)
    HANW002111 = Column("HANW002111", DECIMAL, nullable=False, default=0)
    HANW002112 = Column("HANW002112", DECIMAL(19, 4), nullable=False, default=0)
    HANW002113 = Column("HANW002113", DECIMAL(19, 4), nullable=False, default=0)
    HANW002114 = Column("HANW002114", DECIMAL(19, 4), nullable=False, default=0)
    HANW002115 = Column("HANW002115", DECIMAL(19, 4), nullable=False, default=0)
    HANW002116 = Column("HANW002116", DECIMAL(19, 4), nullable=False, default=0)
    
    # More decimal columns
    HANW002117 = Column("HANW002117", DECIMAL, nullable=False, default=0)
    HANW002118 = Column("HANW002118", DECIMAL, nullable=False, default=0)
    HANW002119 = Column("HANW002119", DECIMAL, nullable=False, default=0)
    
    # Nullable string
    HANW002120 = Column("HANW002120", NVARCHAR(36), nullable=True)
    
    # Regular decimal column
    HANW002121 = Column("HANW002121", DECIMAL, nullable=False, default=0)
    
    # A series of columns with special prefix
    HANW002A001 = Column("HANW002A001", CHAR(4), nullable=False, default='')
    HANW002A002 = Column("HANW002A002", CHAR(2), nullable=False, default='')
    HANW002A003 = Column("HANW002A003", CHAR(2), nullable=False, default='')
    HANW002A004 = Column("HANW002A004", CHAR(2), nullable=False, default='')
    HANW002A005 = Column("HANW002A005", CHAR(2), nullable=False, default='')
    HANW002A006 = Column("HANW002A006", CHAR(2), nullable=False, default='')
    HANW002A007 = Column("HANW002A007", DECIMAL, nullable=False, default=0)
    HANW002A008 = Column("HANW002A008", DECIMAL, nullable=False, default=0)
    HANW002A009 = Column("HANW002A009", DECIMAL, nullable=False, default=0)
    HANW002A010 = Column("HANW002A010", DECIMAL, nullable=False, default=0)
    HANW002A011 = Column("HANW002A011", DECIMAL, nullable=False, default=0)
    HANW002A012 = Column("HANW002A012", DECIMAL, nullable=False, default=0)
    
    # Relationship to header
    picking_header = relationship("FujiTradingPickingManagement", back_populates="picking_works")

    def __repr__(self):
        return f"<HAN10W002PICKINGW {self.HANW002001}-{self.HANW002002}-{self.HANW002003}-{self.HANW002078}>" 