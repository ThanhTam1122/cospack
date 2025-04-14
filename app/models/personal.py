from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.types import DECIMAL
from sqlalchemy.dialects.mssql import NVARCHAR, CHAR
from app.db.base import Base

class Personal(Base):
    """
    Personal Master
    """
    __tablename__ = "HAN10M004TANTO"

    # Main Fields
    HANM004001 = Column("HANM004001", CHAR(8), primary_key=True, nullable=False)  # 担当者コード
    HANM004002 = Column("HANM004002", NVARCHAR(24))   # 担当者名
    HANM004003 = Column("HANM004003", NVARCHAR(8))    # 担当者略称
    HANM004004 = Column("HANM004004", CHAR(24), nullable=False)  # 担当者フリガナ
    
    # 分類コード0-9
    HANM004005 = Column("HANM004005", CHAR(8), nullable=False)
    HANM004006 = Column("HANM004006", CHAR(8), nullable=False)
    HANM004007 = Column("HANM004007", CHAR(8), nullable=False)
    HANM004008 = Column("HANM004008", CHAR(8), nullable=False)
    HANM004009 = Column("HANM004009", CHAR(8), nullable=False)
    HANM004010 = Column("HANM004010", CHAR(8), nullable=False)
    HANM004011 = Column("HANM004011", CHAR(8), nullable=False)
    HANM004012 = Column("HANM004012", CHAR(8), nullable=False)
    HANM004013 = Column("HANM004013", CHAR(8), nullable=False)
    HANM004014 = Column("HANM004014", CHAR(8), nullable=False)
    
    # 部門コード
    HANM004015 = Column("HANM004015", CHAR(8), nullable=False)
    
    # 表示区分
    HANM004016 = Column("HANM004016", DECIMAL, nullable=False, default=0)
    
    # 可変長テキストフィールド
    HANM004K001 = Column("HANM004K001", NVARCHAR(256))  # 表示順
    HANM004K002 = Column("HANM004K002", NVARCHAR(256))  # メールアドレス1
    HANM004K003 = Column("HANM004K003", NVARCHAR(256))  # メールアドレス2
    HANM004K004 = Column("HANM004K004", NVARCHAR(256))  # 拡張項目４
    HANM004K005 = Column("HANM004K005", NVARCHAR(256))
    HANM004K006 = Column("HANM004K006", NVARCHAR(256))
    HANM004K007 = Column("HANM004K007", NVARCHAR(256))
    HANM004K008 = Column("HANM004K008", NVARCHAR(256))
    HANM004K009 = Column("HANM004K009", NVARCHAR(256))
    HANM004K010 = Column("HANM004K010", NVARCHAR(256))
    HANM004K011 = Column("HANM004K011", NVARCHAR(256))
    HANM004K012 = Column("HANM004K012", NVARCHAR(256))
    HANM004K013 = Column("HANM004K013", NVARCHAR(256))
    HANM004K014 = Column("HANM004K014", NVARCHAR(256))
    HANM004K015 = Column("HANM004K015", NVARCHAR(256))
    HANM004K016 = Column("HANM004K016", NVARCHAR(256))
    HANM004K017 = Column("HANM004K017", NVARCHAR(256))
    HANM004K018 = Column("HANM004K018", NVARCHAR(256))
    HANM004K019 = Column("HANM004K019", NVARCHAR(256))
    HANM004K020 = Column("HANM004K020", NVARCHAR(256))

    # 付箋色番号
    HANM004K999 = Column("HANM004K999", DECIMAL, nullable=False, default=0)

    # 更新番号
    HANM004999 = Column("HANM004999", DECIMAL, nullable=False, default=0)

    # 変更履歴
    HANM004901 = Column("HANM004901", CHAR(8), nullable=False)  # 初期担当者コード
    HANM004902 = Column("HANM004902", DECIMAL, nullable=False, default=0)  # 内連番

    # 登録日時・更新日時
    HANM004INS = Column("HANM004INS", DECIMAL(20, 6), nullable=False)
    HANM004UPD = Column("HANM004UPD", DECIMAL(20, 6), nullable=False)

    # 有効期間
    HANM004017 = Column("HANM004017", DECIMAL, nullable=False, default=0)  # 開始日
    HANM004018 = Column("HANM004018", DECIMAL, nullable=False, default=0)  # 終了日
