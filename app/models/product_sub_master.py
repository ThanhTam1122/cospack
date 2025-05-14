from sqlalchemy import Column
from sqlalchemy.types import DECIMAL
from sqlalchemy.dialects.mssql import NVARCHAR, CHAR
from sqlalchemy.sql.expression import text
from app.db.base import Base

class ProductSubMaster(Base):
    """
    商品サブマスタ (HAN99MA33SHOHINSUB)
    Product Sub Master
    """
    __tablename__ = "HAN99MA33SHOHINSUB"
    
    # Primary key and basic product information
    HANMA33001 = Column("HANMA33001", DECIMAL, primary_key=True, nullable=False)  # 商品コード
    
    # Tax information
    HANMA33002 = Column("HANMA33002", NVARCHAR(32))  # 税番１
    HANMA33003 = Column("HANMA33003", NVARCHAR(32))  # 税番２
    HANMA33005 = Column("HANMA33005", NVARCHAR(32))  # 税番３
    HANMA33006 = Column("HANMA33006", DECIMAL(15, 4), nullable=False, default=0)  # 税率１
    HANMA33007 = Column("HANMA33007", DECIMAL(15, 4), nullable=False, default=0)  # 税率２
    HANMA33008 = Column("HANMA33008", DECIMAL(15, 4), nullable=False, default=0)  # 税率３
    
    # Other legal and preference information
    HANMA33009 = Column("HANMA33009", NVARCHAR(32))  # 他法令１
    HANMA33010 = Column("HANMA33010", NVARCHAR(32))  # 他法令２
    HANMA33011 = Column("HANMA33011", NVARCHAR(32))  # 他法令３
    HANMA33012 = Column("HANMA33012", NVARCHAR(32))  # 特恵１
    HANMA33013 = Column("HANMA33013", NVARCHAR(32))  # 特恵２
    HANMA33014 = Column("HANMA33014", NVARCHAR(32))  # 特恵３
    HANMA33015 = Column("HANMA33015", NVARCHAR(1000))  # 備考１
    
    # Factory and order information
    HANMA33064 = Column("HANMA33064", CHAR(11), nullable=False, default='')  # 工場コード
    HANMA33088 = Column("HANMA33088", DECIMAL(15, 4), nullable=False, default=0)  # FOR_NTD
    HANMA33016 = Column("HANMA33016", DECIMAL(7, 0), nullable=False, default=0)  # 最小発注ロット
    HANMA33065 = Column("HANMA33065", DECIMAL(1, 0), nullable=False, default=0)  # 発注継続区分
    
    # Unused fields
    HANMA33063 = Column("HANMA33063", DECIMAL(15, 4), nullable=False, default=0)  # 【未使用】チャーター下代
    HANMA33017 = Column("HANMA33017", DECIMAL(15, 4), nullable=False, default=0)  # 【未使用】特価下代
    
    # Product attributes
    HANMA33018 = Column("HANMA33018", DECIMAL(4, 0), nullable=False, default=0)  # PCサイズ
    HANMA33019 = Column("HANMA33019", DECIMAL(2, 0), nullable=False, default=0)  # ライセンス区分
    HANMA33020 = Column("HANMA33020", DECIMAL(2, 0), nullable=False, default=0)  # 返品対応区分
    HANMA33021 = Column("HANMA33021", DECIMAL(2, 0), nullable=False, default=0)  # 商品形態
    
    # External box 1 specifications
    HANMA33022 = Column("HANMA33022", DECIMAL(9, 0), nullable=False, default=0)  # 外箱1W
    HANMA33023 = Column("HANMA33023", DECIMAL(9, 0), nullable=False, default=0)  # 外箱1D
    HANMA33024 = Column("HANMA33024", DECIMAL(9, 0), nullable=False, default=0)  # 外箱1H
    HANMA33025 = Column("HANMA33025", DECIMAL(9, 0), nullable=False, default=0)  # 外箱1GW
    HANMA33026 = Column("HANMA33026", CHAR(8), nullable=False, default='')  # 外箱1梱包形態
    
    # External box 2 specifications
    HANMA33027 = Column("HANMA33027", DECIMAL(9, 0), nullable=False, default=0)  # 外箱2W
    HANMA33028 = Column("HANMA33028", DECIMAL(9, 0), nullable=False, default=0)  # 外箱2D
    HANMA33029 = Column("HANMA33029", DECIMAL(9, 0), nullable=False, default=0)  # 外箱2H
    HANMA33030 = Column("HANMA33030", DECIMAL(9, 0), nullable=False, default=0)  # 外箱2GW
    HANMA33031 = Column("HANMA33031", CHAR(8), nullable=False, default='')  # 外箱2梱包形態
    
    # External box 3 specifications
    HANMA33032 = Column("HANMA33032", DECIMAL(9, 0), nullable=False, default=0)  # 外箱3W
    HANMA33033 = Column("HANMA33033", DECIMAL(9, 0), nullable=False, default=0)  # 外箱3D
    HANMA33034 = Column("HANMA33034", DECIMAL(9, 0), nullable=False, default=0)  # 外箱3H
    HANMA33035 = Column("HANMA33035", DECIMAL(9, 0), nullable=False, default=0)  # 外箱3GW
    HANMA33036 = Column("HANMA33036", CHAR(8), nullable=False, default='')  # 外箱3梱包形態
    
    # External box 4 specifications
    HANMA33037 = Column("HANMA33037", DECIMAL(9, 0), nullable=False, default=0)  # 外箱4W
    HANMA33038 = Column("HANMA33038", DECIMAL(9, 0), nullable=False, default=0)  # 外箱4D
    HANMA33039 = Column("HANMA33039", DECIMAL(9, 0), nullable=False, default=0)  # 外箱4H
    HANMA33040 = Column("HANMA33040", DECIMAL(9, 0), nullable=False, default=0)  # 外箱4GW
    HANMA33041 = Column("HANMA33041", CHAR(8), nullable=False, default='')  # 外箱4梱包形態
    
    # External box 5 specifications
    HANMA33042 = Column("HANMA33042", DECIMAL(9, 0), nullable=False, default=0)  # 外箱5W
    HANMA33043 = Column("HANMA33043", DECIMAL(9, 0), nullable=False, default=0)  # 外箱5D
    HANMA33044 = Column("HANMA33044", DECIMAL(9, 0), nullable=False, default=0)  # 外箱5H
    HANMA33045 = Column("HANMA33045", DECIMAL(9, 0), nullable=False, default=0)  # 外箱5GW
    HANMA33046 = Column("HANMA33046", CHAR(8), nullable=False, default='')  # 外箱5梱包形態
    
    # Inner box specifications
    HANMA33047 = Column("HANMA33047", DECIMAL(9, 0), nullable=False, default=0)  # 内箱W
    HANMA33048 = Column("HANMA33048", DECIMAL(9, 0), nullable=False, default=0)  # 内箱D
    HANMA33049 = Column("HANMA33049", DECIMAL(9, 0), nullable=False, default=0)  # 内箱H
    HANMA33050 = Column("HANMA33050", DECIMAL(9, 0), nullable=False, default=0)  # 内箱GW
    HANMA33051 = Column("HANMA33051", CHAR(8), nullable=False, default='')  # 内箱梱包形態
    
    # Individual packaging specifications
    HANMA33052 = Column("HANMA33052", DECIMAL(9, 0), nullable=False, default=0)  # 個包装W
    HANMA33053 = Column("HANMA33053", DECIMAL(9, 0), nullable=False, default=0)  # 個包装D
    HANMA33054 = Column("HANMA33054", DECIMAL(9, 0), nullable=False, default=0)  # 個包装H
    HANMA33055 = Column("HANMA33055", DECIMAL(9, 0), nullable=False, default=0)  # 個包装GW
    HANMA33056 = Column("HANMA33056", CHAR(8), nullable=False, default='')  # 個包装梱包形態
    
    # Detailed size information
    HANMA33066 = Column("HANMA33066", NVARCHAR(20))  # 詳細サイズ名称1
    HANMA33067 = Column("HANMA33067", NVARCHAR(20))  # 詳細サイズ1
    HANMA33068 = Column("HANMA33068", NVARCHAR(20))  # 詳細サイズ名称2
    HANMA33069 = Column("HANMA33069", NVARCHAR(20))  # 詳細サイズ2
    HANMA33070 = Column("HANMA33070", NVARCHAR(20))  # 詳細サイズ名称3
    HANMA33071 = Column("HANMA33071", NVARCHAR(20))  # 詳細サイズ3
    HANMA33072 = Column("HANMA33072", NVARCHAR(20))  # 詳細サイズ名称4
    HANMA33073 = Column("HANMA33073", NVARCHAR(20))  # 詳細サイズ4
    HANMA33074 = Column("HANMA33074", NVARCHAR(20))  # 詳細サイズ名称5
    HANMA33075 = Column("HANMA33075", NVARCHAR(20))  # 詳細サイズ5
    HANMA33076 = Column("HANMA33076", NVARCHAR(20))  # 詳細サイズ名称6
    HANMA33077 = Column("HANMA33077", NVARCHAR(20))  # 詳細サイズ6
    HANMA33078 = Column("HANMA33078", NVARCHAR(20))  # 詳細サイズ名称7
    HANMA33079 = Column("HANMA33079", NVARCHAR(20))  # 詳細サイズ7
    HANMA33080 = Column("HANMA33080", NVARCHAR(20))  # 詳細サイズ名称8
    HANMA33081 = Column("HANMA33081", NVARCHAR(20))  # 詳細サイズ8
    HANMA33082 = Column("HANMA33082", NVARCHAR(20))  # 詳細サイズ名称9
    HANMA33083 = Column("HANMA33083", NVARCHAR(20))  # 詳細サイズ9
    HANMA33084 = Column("HANMA33084", NVARCHAR(20))  # 詳細サイズ名称10
    HANMA33085 = Column("HANMA33085", NVARCHAR(20))  # 詳細サイズ10
    
    # Material and remarks
    HANMA33086 = Column("HANMA33086", NVARCHAR(500))  # 材質
    HANMA33087 = Column("HANMA33087", NVARCHAR(500))  # 備考
    
    # Shipping fee information
    HANMA33057 = Column("HANMA33057", DECIMAL(9, 0), nullable=False, default=0)  # 統一運賃
    HANMA33058 = Column("HANMA33058", DECIMAL(9, 0), nullable=False, default=0)  # 北海道運賃
    HANMA33059 = Column("HANMA33059", DECIMAL(9, 0), nullable=False, default=0)  # 沖縄本島運賃
    HANMA33060 = Column("HANMA33060", DECIMAL(2, 0), nullable=False, default=0)  # 配送区分
    
    # Timestamps and update information
    HANMA33INS = Column("HANMA33INS", DECIMAL(14, 6), nullable=False, 
                       default=text("CONVERT([decimal](14,6),replace(replace(replace(CONVERT([nvarchar](40),getdate(),(121)),'-',''),':',''),' ',''))"))  # 登録日時
    HANMA33UPD = Column("HANMA33UPD", DECIMAL(14, 6), nullable=False,
                       default=text("CONVERT([decimal](14,6),replace(replace(replace(CONVERT([nvarchar](40),getdate(),(121)),'-',''),':',''),' ',''))"))  # 更新日時
    HANMA33999 = Column("HANMA33999", DECIMAL(9, 0), nullable=False, default=0)  # 更新番号
    
    # Product image and distribution information
    HANMA33061 = Column("HANMA33061", NVARCHAR(128))  # 商品画像URL
    HANMA33062 = Column("HANMA33062", DECIMAL(2, 0), nullable=False, default=0)  # 販路区分
    HANMA33131 = Column("HANMA33131", DECIMAL(1, 0), nullable=False, default=0)  # ドロップシップ可否
    
    # Product description and image fields
    HANMA33089 = Column("HANMA33089", NVARCHAR(120))  # キャッチコピー
    HANMA33090 = Column("HANMA33090", NVARCHAR(128))  # 画像MAIN
    
    # Product leads, bodies, and images (1-6)
    HANMA33091 = Column("HANMA33091", NVARCHAR(44))  # リード1
    HANMA33092 = Column("HANMA33092", NVARCHAR(180))  # ボディ1
    HANMA33093 = Column("HANMA33093", NVARCHAR(128))  # 画像1
    HANMA33094 = Column("HANMA33094", NVARCHAR(44))  # リード2
    HANMA33095 = Column("HANMA33095", NVARCHAR(180))  # ボディ2
    HANMA33096 = Column("HANMA33096", NVARCHAR(128))  # 画像2
    HANMA33097 = Column("HANMA33097", NVARCHAR(44))  # リード3
    HANMA33098 = Column("HANMA33098", NVARCHAR(180))  # ボディ3
    HANMA33099 = Column("HANMA33099", NVARCHAR(128))  # 画像3
    HANMA33100 = Column("HANMA33100", NVARCHAR(44))  # リード4
    HANMA33101 = Column("HANMA33101", NVARCHAR(180))  # ボディ4
    HANMA33102 = Column("HANMA33102", NVARCHAR(128))  # 画像4
    HANMA33103 = Column("HANMA33103", NVARCHAR(44))  # リード5
    HANMA33104 = Column("HANMA33104", NVARCHAR(180))  # ボディ5
    HANMA33105 = Column("HANMA33105", NVARCHAR(128))  # 画像5
    HANMA33106 = Column("HANMA33106", NVARCHAR(44))  # リード6
    HANMA33107 = Column("HANMA33107", NVARCHAR(180))  # ボディ6
    HANMA33108 = Column("HANMA33108", NVARCHAR(128))  # 画像6
    
    # Color variations (1-10)
    HANMA33109 = Column("HANMA33109", NVARCHAR(8))  # カラバリ1
    HANMA33110 = Column("HANMA33110", NVARCHAR(128))  # カラバリ1画像
    HANMA33111 = Column("HANMA33111", NVARCHAR(8))  # カラバリ2
    HANMA33112 = Column("HANMA33112", NVARCHAR(128))  # カラバリ2画像
    HANMA33113 = Column("HANMA33113", NVARCHAR(8))  # カラバリ3
    HANMA33114 = Column("HANMA33114", NVARCHAR(128))  # カラバリ3画像
    HANMA33115 = Column("HANMA33115", NVARCHAR(8))  # カラバリ4
    HANMA33116 = Column("HANMA33116", NVARCHAR(128))  # カラバリ4画像
    HANMA33117 = Column("HANMA33117", NVARCHAR(8))  # カラバリ5
    HANMA33118 = Column("HANMA33118", NVARCHAR(128))  # カラバリ5画像
    HANMA33119 = Column("HANMA33119", NVARCHAR(8))  # カラバリ6
    HANMA33120 = Column("HANMA33120", NVARCHAR(128))  # カラバリ6画像
    HANMA33121 = Column("HANMA33121", NVARCHAR(8))  # カラバリ7
    HANMA33122 = Column("HANMA33122", NVARCHAR(128))  # カラバリ7画像
    HANMA33123 = Column("HANMA33123", NVARCHAR(8))  # カラバリ8
    HANMA33124 = Column("HANMA33124", NVARCHAR(128))  # カラバリ8画像
    HANMA33125 = Column("HANMA33125", NVARCHAR(8))  # カラバリ9
    HANMA33126 = Column("HANMA33126", NVARCHAR(128))  # カラバリ9画像
    HANMA33127 = Column("HANMA33127", NVARCHAR(8))  # カラバリ10
    HANMA33128 = Column("HANMA33128", NVARCHAR(128))  # カラバリ10画像
    
    # Additional fields
    HANMA33129 = Column("HANMA33129", NVARCHAR(10))  # 統一企画書区分
    HANMA33130 = Column("HANMA33130", CHAR(8), nullable=False, default='')  # シリーズコード
    
    def __repr__(self):
        return f"<ProductSubMaster {self.HANMA33001}>" 