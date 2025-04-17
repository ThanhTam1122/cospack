from sqlalchemy import Column, Integer, String, Date, Boolean, Float
from sqlalchemy.types import DECIMAL
from sqlalchemy.dialects.mssql import NVARCHAR, CHAR, VARCHAR
from sqlalchemy.sql.expression import text
from app.db.base import Base

class ProductMaster(Base):
    """
    商品マスター (HAN10M003SHOHIN)
    Product Master
    """
    __tablename__ = "HAN10M003SHOHIN"
    
    # Primary key and basic product information
    HANM003001 = Column("HANM003001", DECIMAL, primary_key=True, nullable=False)  # 商品コード
    HANM003002 = Column("HANM003002", NVARCHAR(36))  # 商品略称
    HANM003003 = Column("HANM003003", CHAR(10), nullable=False, default='')  # 商品索引
    HANM003004 = Column("HANM003004", NVARCHAR(4))  # 単位
    HANM003005 = Column("HANM003005", NVARCHAR(4))  # 個数単位
    HANM003006 = Column("HANM003006", DECIMAL(15, 4), nullable=False, default=0)  # 入数
    HANM003007 = Column("HANM003007", DECIMAL(1, 0), nullable=False, default=0)  # セット品区分
    HANM003008 = Column("HANM003008", DECIMAL(1, 0), nullable=False, default=0)  # 在庫管理区分
    
    # Pricing fields
    HANM003009 = Column("HANM003009", DECIMAL(15, 4), nullable=False, default=0)  # 標準売上単価
    HANM003010 = Column("HANM003010", DECIMAL(15, 4), nullable=False, default=0)  # ランク１売上単価
    HANM003011 = Column("HANM003011", DECIMAL(15, 4), nullable=False, default=0)  # ランク２売上単価
    HANM003012 = Column("HANM003012", DECIMAL(15, 4), nullable=False, default=0)  # ランク３売上単価
    HANM003013 = Column("HANM003013", DECIMAL(15, 4), nullable=False, default=0)  # ランク４売上単価
    HANM003014 = Column("HANM003014", DECIMAL(15, 4), nullable=False, default=0)  # ランク５売上単価
    HANM003015 = Column("HANM003015", DECIMAL(15, 4), nullable=False, default=0)  # 標準仕入単価
    HANM003016 = Column("HANM003016", DECIMAL(15, 4), nullable=False, default=0)  # 在庫評価単価
    HANM003017 = Column("HANM003017", DECIMAL(15, 4), nullable=False, default=0)  # 粗利算出用原単価
    HANM003018 = Column("HANM003018", DECIMAL(15, 4), nullable=False, default=0)  # 上代単価
    
    # Classification fields
    HANM003019 = Column("HANM003019", CHAR(8), nullable=False, default='')  # 定番区分
    HANM003020 = Column("HANM003020", CHAR(8), nullable=False, default='')  # 原産国
    HANM003021 = Column("HANM003021", CHAR(8), nullable=False, default='')  # 大カテゴリ
    HANM003022 = Column("HANM003022", CHAR(8), nullable=False, default='')  # 中カテゴリ
    HANM003023 = Column("HANM003023", CHAR(8), nullable=False, default='')  # 小カテゴリ
    HANM003024 = Column("HANM003024", CHAR(8), nullable=False, default='')  # TOSS連携用
    HANM003025 = Column("HANM003025", CHAR(8), nullable=False, default='')  # 商品担当者
    HANM003026 = Column("HANM003026", CHAR(8), nullable=False, default='')  # 汎用分類
    HANM003027 = Column("HANM003027", CHAR(8), nullable=False, default='')  # ｾﾝﾀｰｶﾃｺﾞﾘ
    HANM003028 = Column("HANM003028", CHAR(8), nullable=False, default='')  # 分類コード９
    
    # Changed price fields
    HANM003029 = Column("HANM003029", DECIMAL(15, 4), nullable=False, default=0)  # 変更後単価－標準売上単価
    HANM003030 = Column("HANM003030", DECIMAL(15, 4), nullable=False, default=0)  # 変更後単価－ランク１売上単価
    HANM003031 = Column("HANM003031", DECIMAL(15, 4), nullable=False, default=0)  # 変更後単価－ランク２売上単価
    HANM003032 = Column("HANM003032", DECIMAL(15, 4), nullable=False, default=0)  # 変更後単価－ランク３売上単価
    HANM003033 = Column("HANM003033", DECIMAL(15, 4), nullable=False, default=0)  # 変更後単価－ランク４売上単価
    HANM003034 = Column("HANM003034", DECIMAL(15, 4), nullable=False, default=0)  # 変更後単価－ランク５売上単価
    HANM003035 = Column("HANM003035", DECIMAL(15, 4), nullable=False, default=0)  # 変更後単価－標準仕入単価
    HANM003036 = Column("HANM003036", DECIMAL(15, 4), nullable=False, default=0)  # 変更後単価－在庫評価単価
    HANM003037 = Column("HANM003037", DECIMAL(15, 4), nullable=False, default=0)  # 変更後単価－粗利算出用原単価
    HANM003038 = Column("HANM003038", DECIMAL(15, 4), nullable=False, default=0)  # 変更後単価－上代単価
    
    # Date and price settings
    HANM003039 = Column("HANM003039", DECIMAL(8, 0), nullable=False, default=0)  # 単価変更日付
    HANM003040 = Column("HANM003040", DECIMAL(8, 0), nullable=False, default=0)  # 期間単価対象日付（ＴＯ）
    HANM003041 = Column("HANM003041", DECIMAL(1, 0), nullable=False, default=0)  # 変更後単価使用区分
    HANM003042 = Column("HANM003042", DECIMAL(1, 0), nullable=False, default=0)  # 消費税－非課税区分
    HANM003043 = Column("HANM003043", DECIMAL(1, 0), nullable=False, default=0)  # 消費税－売上単価設定区分
    HANM003044 = Column("HANM003044", DECIMAL(1, 0), nullable=False, default=0)  # 消費税－仕入単価設定区分
    HANM003045 = Column("HANM003045", DECIMAL(2, 0), nullable=False, default=0)  # 消費税ー消費税率区分
    HANM003046 = Column("HANM003046", DECIMAL(1, 0), nullable=False, default=0)  # 出荷管理－直送区分
    HANM003047 = Column("HANM003047", DECIMAL(15, 4), nullable=False, default=0)  # 出荷管理－適正在庫数量
    HANM003048 = Column("HANM003048", DECIMAL(1, 0), nullable=False, default=0)  # Ｆ
    HANM003049 = Column("HANM003049", DECIMAL(1, 0), nullable=False, default=0)  # CONTACT－チェーンストア区分
    HANM003050 = Column("HANM003050", DECIMAL(1, 0), nullable=False, default=0)  # マスター検索表示区分
    
    # Detail management
    HANM003051 = Column("HANM003051", DECIMAL(1, 0), nullable=False, default=0)  # 内訳管理－内訳管理区分－種別１
    HANM003052 = Column("HANM003052", DECIMAL(1, 0), nullable=False, default=0)  # 内訳管理－内訳管理区分－種別２
    HANM003053 = Column("HANM003053", DECIMAL(1, 0), nullable=False, default=0)  # 内訳管理－内訳管理区分－種別３
    HANM003054 = Column("HANM003054", DECIMAL(1, 0), nullable=False, default=0)  # 在庫引当対象区分
    HANM003055 = Column("HANM003055", DECIMAL(1, 0), nullable=False, default=0)  # 消費税総額－上代単価設定区分
    HANM003056 = Column("HANM003056", DECIMAL(1, 0), nullable=False, default=0)  # 消費税総額－変更後売上単価設定区分
    HANM003057 = Column("HANM003057", DECIMAL(1, 0), nullable=False, default=0)  # 消費税総額－変更後仕入単価設定区分
    HANM003058 = Column("HANM003058", DECIMAL(1, 0), nullable=False, default=0)  # 消費税総額－変更後上代単価設定区分
    
    # Tax calculation settings
    HANM003059 = Column("HANM003059", DECIMAL(1, 0), nullable=False, default=0)  # 消費税総額－売上単価税込変換計算区分
    HANM003060 = Column("HANM003060", DECIMAL(9, 0), nullable=False, default=0)  # 消費税総額－売上単価税込変換計算単位
    HANM003061 = Column("HANM003061", DECIMAL(1, 0), nullable=False, default=0)  # 消費税総額－売上単価税抜変換計算区分
    HANM003062 = Column("HANM003062", DECIMAL(9, 0), nullable=False, default=0)  # 消費税総額－売上単価税抜変換計算単位
    HANM003063 = Column("HANM003063", DECIMAL(1, 0), nullable=False, default=0)  # 消費税総額－仕入単価税込変換計算区分
    HANM003064 = Column("HANM003064", DECIMAL(9, 0), nullable=False, default=0)  # 消費税総額－仕入単価税込変換計算単位
    HANM003065 = Column("HANM003065", DECIMAL(1, 0), nullable=False, default=0)  # 消費税総額－仕入単価税抜変換計算区分
    HANM003066 = Column("HANM003066", DECIMAL(9, 0), nullable=False, default=0)  # 消費税総額－仕入単価税抜変換計算単位
    HANM003067 = Column("HANM003067", DECIMAL(1, 0), nullable=False, default=0)  # 消費税総額－上代単価税込変換計算区分
    HANM003068 = Column("HANM003068", DECIMAL(9, 0), nullable=False, default=0)  # 消費税総額－上代単価税込変換計算単位
    HANM003069 = Column("HANM003069", DECIMAL(1, 0), nullable=False, default=0)  # 消費税総額－上代単価税抜変換計算区分
    HANM003070 = Column("HANM003070", DECIMAL(9, 0), nullable=False, default=0)  # 消費税総額－上代単価税抜変換計算単位
    
    # Inspection and vendor related
    HANM003071 = Column("HANM003071", DECIMAL(1, 0), nullable=False, default=0)  # 検収基準－売上検収区分
    HANM003072 = Column("HANM003072", DECIMAL(1, 0), nullable=False, default=0)  # 検収基準－仕入検収区分
    HANM003073 = Column("HANM003073", DECIMAL(1, 0), nullable=False, default=0)  # 自動振替処理対象区分
    HANM003074 = Column("HANM003074", CHAR(11), nullable=False, default='')  # 主仕入先コード
    HANM003075 = Column("HANM003075", DECIMAL(1, 0), nullable=False, default=0)  # 在庫評価区分
    HANM003076 = Column("HANM003076", CHAR(4), nullable=False, default='')  # 明細拡張項目入力－パターン№(売上)
    HANM003077 = Column("HANM003077", CHAR(4), nullable=False, default='')  # 明細拡張項目入力－パターン№(仕入)
    
    # Variable text fields (K series)
    HANM003K001 = Column("HANM003K001", NVARCHAR(256))  # ＪＡＮコード
    HANM003K002 = Column("HANM003K002", NVARCHAR(256))  # ＪＡＮコード２
    HANM003K003 = Column("HANM003K003", NVARCHAR(256))  # ＩＴＥＭ№
    HANM003K004 = Column("HANM003K004", NVARCHAR(256))  # 色柄(英文)
    HANM003K005 = Column("HANM003K005", NVARCHAR(256))  # 色柄(和文)
    HANM003K006 = Column("HANM003K006", NVARCHAR(256))  # ×荷姿
    HANM003K007 = Column("HANM003K007", NVARCHAR(256))  # 入数(内箱)
    HANM003K008 = Column("HANM003K008", NVARCHAR(256))  # 入数(外箱)
    HANM003K009 = Column("HANM003K009", NVARCHAR(256))  # 才数
    HANM003K010 = Column("HANM003K010", NVARCHAR(256))  # 出荷単位
    HANM003K011 = Column("HANM003K011", NVARCHAR(256))  # コンテナサイズ
    HANM003K012 = Column("HANM003K012", NVARCHAR(256))  # コンテナ入数
    HANM003K013 = Column("HANM003K013", NVARCHAR(256))  # 通貨
    HANM003K014 = Column("HANM003K014", NVARCHAR(256))  # 雑貨区分
    HANM003K015 = Column("HANM003K015", NVARCHAR(256))  # 商品フォルダ
    HANM003K016 = Column("HANM003K016", NVARCHAR(256))  # 商品パス
    HANM003K017 = Column("HANM003K017", NVARCHAR(256))  # 最終通関日
    HANM003K018 = Column("HANM003K018", NVARCHAR(256))  # 必要書類区分
    HANM003K019 = Column("HANM003K019", NVARCHAR(256))  # 初回入荷日
    HANM003K020 = Column("HANM003K020", NVARCHAR(256))  # TOSS按分区分
    
    # Additional fields and system management
    HANM003K999 = Column("HANM003K999", DECIMAL(1, 0), nullable=False, default=0)  # 付箋色番号
    HANM003998 = Column("HANM003998", DECIMAL(4, 0), nullable=False, default=0)  # 年次更新済年
    HANM003999 = Column("HANM003999", DECIMAL(9, 0), nullable=False, default=0)  # 更新番号
    HANM003078 = Column("HANM003078", DECIMAL(1, 0), nullable=False, default=0)  # 原価管理－仕入時原価集計入力
    
    # Change history
    HANM003901 = Column("HANM003901", DECIMAL, nullable=False, default=0)  # 変更履歴－初期商品コード
    HANM003902 = Column("HANM003902", DECIMAL(4, 0), nullable=False, default=0)  # 変更履歴－初期商品コード内連番
    
    # Product detail settings
    HANM003079 = Column("HANM003079", CHAR(20), nullable=False, default='')  # 商品内訳－内訳種別１ 初期値
    HANM003080 = Column("HANM003080", CHAR(20), nullable=False, default='')  # 商品内訳－内訳種別２ 初期値
    HANM003081 = Column("HANM003081", CHAR(20), nullable=False, default='')  # 商品内訳－内訳種別３ 初期値
    HANM003082 = Column("HANM003082", NVARCHAR(4))  # 商品内訳－内訳（数値）種別１ 単位
    HANM003083 = Column("HANM003083", NVARCHAR(4))  # 商品内訳－内訳（数値）種別２ 単位
    HANM003084 = Column("HANM003084", NVARCHAR(4))  # 商品内訳－内訳（数値）種別３ 単位
    HANM003085 = Column("HANM003085", DECIMAL(1, 0), nullable=False, default=0)  # 在庫引当単位
    
    # Conversion quantity settings
    HANM003086 = Column("HANM003086", DECIMAL(1, 0), nullable=False, default=0)  # 換算数量－換算数量使用区分
    HANM003087 = Column("HANM003087", NVARCHAR(4))  # 換算数量－換算数量単位
    HANM003088 = Column("HANM003088", DECIMAL(5, 6), nullable=False, default=0)  # 換算数量－換算係数
    HANM003089 = Column("HANM003089", CHAR(4), nullable=False, default='')  # 換算数量－換算数量計算パターン№
    HANM003090 = Column("HANM003090", DECIMAL(1, 0), nullable=False, default=0)  # 換算数量－換算数量計算区分
    HANM003091 = Column("HANM003091", DECIMAL(9, 0), nullable=False, default=0)  # 換算数量－換算数量計算単位
    
    # Lot management
    HANM003092 = Column("HANM003092", DECIMAL(1, 0), nullable=False, default=0)  # ロット管理－ロット管理区分
    HANM003093 = Column("HANM003093", DECIMAL(1, 0), nullable=False, default=0)  # ロット管理－在庫評価算出単位
    HANM003094 = Column("HANM003094", DECIMAL(4, 0), nullable=False, default=0)  # ロット管理－有効日数
    HANM003095 = Column("HANM003095", DECIMAL(3, 0), nullable=False, default=0)  # ロット管理－警告表示開始日
    
    # Timestamps and validity period
    HANM003INS = Column("HANM003INS", DECIMAL(20, 6), nullable=False, 
                      default=text("CONVERT([decimal](20,6),replace(replace(replace(CONVERT([nvarchar](40),getdate(),(121)),'-',''),':',''),' ',''))"))  # 登録日時
    HANM003UPD = Column("HANM003UPD", DECIMAL(20, 6), nullable=False,
                      default=text("CONVERT([decimal](20,6),replace(replace(replace(CONVERT([nvarchar](40),getdate(),(121)),'-',''),':',''),' ',''))"))  # 更新日時
    HANM003096 = Column("HANM003096", DECIMAL(8, 0), nullable=False, default=0)  # 有効期間－開始日
    HANM003097 = Column("HANM003097", DECIMAL(8, 0), nullable=False, default=0)  # 有効期間－終了日
    
    # Trading patterns and tax rate
    HANM003098 = Column("HANM003098", CHAR(4), nullable=False, default='')  # 汎用在庫－取引パターン（売上）
    HANM003099 = Column("HANM003099", CHAR(4), nullable=False, default='')  # 汎用在庫－取引パターン（仕入）
    HANM003100 = Column("HANM003100", DECIMAL(2, 0), nullable=False, default=0)  # 商品副税率－副消費税率区分
    HANM003101 = Column("HANM003101", DECIMAL(8, 0), nullable=False, default=0)  # 操作日付－操作日付(年月日)
    HANM003102 = Column("HANM003102", NVARCHAR(64))  # 操作日付－ログインID
    
    # Product names extended
    HANM003103 = Column("HANM003103", NVARCHAR(36))  # 商品名１
    HANM003104 = Column("HANM003104", NVARCHAR(36))  # 商品名２
    HANM003001S = Column("HANM003001S", CHAR(25), nullable=False, default='')  # スマートサーチ－商品コード(ゼロサプレス)
    
    # Extended attributes part 1
    HANM003A001 = Column("HANM003A001", NVARCHAR(50))  # 商品名(英文)
    HANM003A002 = Column("HANM003A002", NVARCHAR(50))  # 商品名(和文)
    HANM003A003 = Column("HANM003A003", CHAR(20), nullable=False, default='')  # 塗装
    HANM003A004 = Column("HANM003A004", CHAR(20), nullable=False, default='')  # 材質
    HANM003A005 = Column("HANM003A005", DECIMAL(2, 0), nullable=False, default=0)  # セット個口数量
    HANM003A006 = Column("HANM003A006", DECIMAL(7, 0), nullable=False, default=0)  # 重量(g)
    HANM003A007 = Column("HANM003A007", DECIMAL(7, 0), nullable=False, default=0)  # 梱包重量(g)
    
    # Only including a subset of extended attributes due to character limit constraints
    # The complete set would continue from HANM003A008 through HANM003A109
    
    def __repr__(self):
        return f"<ProductMaster {self.HANM003001}>"