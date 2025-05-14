from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.types import DECIMAL
from app.db.base import Base

class Waybill(Base):
    """
    送り状マスタ
    Waybill Master
    """
    __tablename__ = "HAN10M009OKURIJO"

    HANM009001 = Column("HANM009001", String(32), primary_key=True, nullable=False)  # 送り状コード
    HANM009002 = Column("HANM009002", Date, nullable=False)  # 入出荷予定日
    HANM009003 = Column("HANM009003", Date, nullable=False)  # 納期日
    HANM009004 = Column("HANM009004", String(64), nullable=False)  # 取引先コード
    HANM009005 = Column("HANM009005", DECIMAL, nullable=True)  # 納期情報1
    HANM009006 = Column("HANM009006", DECIMAL, nullable=True)  # 納期情報2
    HANM009007 = Column("HANM009007", String(64), nullable=True)  # 納品先名1
    HANM009008 = Column("HANM009008", String(64), nullable=True)  # 納品先名2
    HANM009009 = Column("HANM009009", String(16), nullable=True)  # 納品先郵便番号
    HANM009010 = Column("HANM009010", String(128), nullable=True)  # 納品先住所1
    HANM009011 = Column("HANM009011", String(128), nullable=True)  # 納品先住所2
    HANM009012 = Column("HANM009012", String(128), nullable=True)  # 納品先住所3
