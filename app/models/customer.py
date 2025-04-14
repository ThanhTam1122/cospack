from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.types import DECIMAL
from sqlalchemy.dialects.mssql import NVARCHAR, CHAR
from app.db.base import Base

class Customer(Base):
    """
    Customer Master (HAN10M001TOKUI - 得意先マスタ)
    """
    __tablename__ = "HAN10M001TOKUI"

    # Primary key and basic info
    HANM001001 = Column("HANM001001", CHAR(11), nullable=False)  # 請求先コード
    HANM001002 = Column("HANM001002", DECIMAL, nullable=False, default=0)  # 請求先区分
    HANM001003 = Column("HANM001003", CHAR(11), primary_key=True, nullable=False)  # 得意先コード
    HANM001004 = Column("HANM001004", NVARCHAR(48))  # 得意先名１
    HANM001005 = Column("HANM001005", NVARCHAR(48))  # 得意先名２
    HANM001006 = Column("HANM001006", NVARCHAR(32))  # 得意先略称
    HANM001007 = Column("HANM001007", CHAR(10), nullable=False)  # 得意先索引
    HANM001008 = Column("HANM001008", CHAR(10), nullable=False)  # 郵便番号
    HANM001009 = Column("HANM001009", NVARCHAR(48))  # 住所１
    HANM001010 = Column("HANM001010", NVARCHAR(48))  # 住所２
    HANM001011 = Column("HANM001011", NVARCHAR(48))  # 住所３
    HANM001012 = Column("HANM001012", CHAR(15), nullable=False)  # 電話番号
    HANM001013 = Column("HANM001013", CHAR(15), nullable=False)  # ＦＡＸ番号
    HANM001014 = Column("HANM001014", CHAR(20), nullable=False)  # カスタマバーコード
    HANM001015 = Column("HANM001015", CHAR(8), nullable=False)  # 担当者コード
    
    # Classification codes
    HANM001016 = Column("HANM001016", CHAR(8), nullable=False)  # 業種
    HANM001017 = Column("HANM001017", CHAR(8), nullable=False)  # グループ
    HANM001018 = Column("HANM001018", CHAR(8), nullable=False)  # 請求方法
    HANM001019 = Column("HANM001019", CHAR(8), nullable=False)  # 取引形態
    HANM001020 = Column("HANM001020", CHAR(8), nullable=False)  # フォロー
    HANM001021 = Column("HANM001021", CHAR(8), nullable=False)  # 分類コード５
    HANM001022 = Column("HANM001022", CHAR(8), nullable=False)  # 分類コード６
    HANM001023 = Column("HANM001023", CHAR(8), nullable=False)  # 分類コード７
    HANM001024 = Column("HANM001024", CHAR(8), nullable=False)  # 分類コード８
    HANM001025 = Column("HANM001025", CHAR(8), nullable=False)  # 分類コード９
    
    # Payment and billing related
    HANM001026 = Column("HANM001026", CHAR(11), nullable=False)  # 相殺仕入先コード
    HANM001027 = Column("HANM001027", DECIMAL, nullable=False, default=0)  # 締日１
    HANM001028 = Column("HANM001028", DECIMAL, nullable=False, default=0)  # 締日２
    HANM001029 = Column("HANM001029", DECIMAL, nullable=False, default=0)  # 締日３
    HANM001030 = Column("HANM001030", DECIMAL, nullable=False, default=0)  # 入金日１
    HANM001031 = Column("HANM001031", DECIMAL, nullable=False, default=0)  # 入金日２
    HANM001032 = Column("HANM001032", DECIMAL, nullable=False, default=0)  # 入金日３
    HANM001033 = Column("HANM001033", DECIMAL, nullable=False, default=0)  # 入金サイクル１
    HANM001034 = Column("HANM001034", DECIMAL, nullable=False, default=0)  # 入金サイクル２
    HANM001035 = Column("HANM001035", DECIMAL, nullable=False, default=0)  # 入金サイクル３
    HANM001036 = Column("HANM001036", DECIMAL, nullable=False, default=0)  # 入金条件１
    HANM001037 = Column("HANM001037", DECIMAL, nullable=False, default=0)  # 入金条件２
    HANM001038 = Column("HANM001038", DECIMAL, nullable=False, default=0)  # 入金条件３
    HANM001039 = Column("HANM001039", DECIMAL(19, 4), nullable=False, default=0)  # 与信限度額
    
    # Pricing related
    HANM001040 = Column("HANM001040", DECIMAL, nullable=False, default=0)  # 売上単価掛率指定－掛率計算区分
    HANM001041 = Column("HANM001041", DECIMAL(4, 1), nullable=False, default=0)  # 売上単価掛率指定－単価掛率
    HANM001042 = Column("HANM001042", DECIMAL, nullable=False, default=0)  # 単価ランク
    
    # Rounding and tax settings
    HANM001043 = Column("HANM001043", DECIMAL, nullable=False, default=0)  # 端数処理－単価－処理区分
    HANM001044 = Column("HANM001044", DECIMAL, nullable=False, default=0)  # 端数処理－単価－処理単位
    HANM001045 = Column("HANM001045", DECIMAL, nullable=False, default=0)  # 端数処理－金額－処理区分
    HANM001046 = Column("HANM001046", DECIMAL, nullable=False, default=0)  # 端数処理－消費税計算－処理区分
    HANM001047 = Column("HANM001047", DECIMAL, nullable=False, default=0)  # 端数処理－消費税計算－処理単位
    HANM001048 = Column("HANM001048", DECIMAL, nullable=False, default=0)  # 端数処理－消費税分解－処理区分
    HANM001049 = Column("HANM001049", DECIMAL, nullable=False, default=0)  # 端数処理－消費税分解－処理単位
    HANM001050 = Column("HANM001050", DECIMAL, nullable=False, default=0)  # 消費税－課税対象区分
    HANM001051 = Column("HANM001051", DECIMAL, nullable=False, default=0)  # 消費税－売上単価設定区分
    HANM001052 = Column("HANM001052", DECIMAL, nullable=False, default=0)  # 消費税－消費税通知区分
    HANM001053 = Column("HANM001053", DECIMAL, nullable=False, default=0)  # 消費税－請求消費税算出単位
    
    # Display and printing preferences
    HANM001054 = Column("HANM001054", DECIMAL, nullable=False, default=0)  # 直前単価優先表示
    HANM001055 = Column("HANM001055", DECIMAL, nullable=False, default=0)  # 日付印字区分
    HANM001056 = Column("HANM001056", DECIMAL, nullable=False, default=0)  # 売上伝票構成品印字区分
    HANM001057 = Column("HANM001057", DECIMAL, nullable=False, default=0)  # 請求書構成品印字区分
    HANM001058 = Column("HANM001058", DECIMAL, nullable=False, default=0)  # 請求書出力タイプ
    HANM001059 = Column("HANM001059", DECIMAL, nullable=False, default=0)  # 請求書出力形式
    HANM001060 = Column("HANM001060", DECIMAL, nullable=False, default=0)  # 得意先台帳出力形式
    
    # Additional fields
    HANM001061 = Column("HANM001061", NVARCHAR(32))  # 相手先担当者名
    HANM001062 = Column("HANM001062", DECIMAL, nullable=False, default=0)  # 回収管理区分
    HANM001063 = Column("HANM001063", CHAR(4), nullable=False)  # 出荷管理－ルートコード
    HANM001064 = Column("HANM001064", DECIMAL, nullable=False, default=0)  # 出荷管理－売上日付区分（出荷管理）
    HANM001065 = Column("HANM001065", DECIMAL, nullable=False, default=0)  # 伝票申請承認－仕訳承認回収消込方法
    HANM001066 = Column("HANM001066", DECIMAL, nullable=False, default=0)  # Ｆ
    HANM001067 = Column("HANM001067", DECIMAL, nullable=False, default=0)  # 指定請求書使用区分
    HANM001068 = Column("HANM001068", DECIMAL, nullable=False, default=0)  # 指定請求書番号
    HANM001069 = Column("HANM001069", DECIMAL(19, 4), nullable=False, default=0)  # Ｆ
    HANM001070 = Column("HANM001070", DECIMAL(19, 4), nullable=False, default=0)  # 前回請求残高
    
    # CONTACT integration fields
    HANM001071 = Column("HANM001071", DECIMAL, nullable=False, default=0)  # CONTACT連動－チェーンストア区分
    HANM001072 = Column("HANM001072", CHAR(8), nullable=False)  # CONTACT連動－売上計上得意先コード
    HANM001073 = Column("HANM001073", CHAR(8), nullable=False)  # CONTACT連動－店舗索引コード
    HANM001074 = Column("HANM001074", CHAR(8), nullable=False)  # CONTACT連動－店舗コード
    
    # More billing and invoice related
    HANM001075 = Column("HANM001075", DECIMAL, nullable=False, default=0)  # 指定請求書番号２
    HANM001076 = Column("HANM001076", DECIMAL, nullable=False, default=0)  # 消費税総額－上代単価設定区分
    HANM001077 = Column("HANM001077", DECIMAL, nullable=False, default=0)  # 消費税総額－単価変換区分
    HANM001078 = Column("HANM001078", DECIMAL, nullable=False, default=0)  # 検収基準－売上検収区分
    HANM001079 = Column("HANM001079", DECIMAL, nullable=False, default=0)  # 取引区分
    
    # Company name references
    HANM001080 = Column("HANM001080", CHAR(4), nullable=False)  # 自社名－売上伝票
    HANM001081 = Column("HANM001081", CHAR(4), nullable=False)  # 自社名－出荷伝票
    HANM001082 = Column("HANM001082", CHAR(4), nullable=False)  # 自社名－請求書
    HANM001083 = Column("HANM001083", CHAR(4), nullable=False)  # 自社名－見積書
    
    # More configs
    HANM001084 = Column("HANM001084", DECIMAL, nullable=False, default=0)  # マスター検索表示区分
    HANM001085 = Column("HANM001085", DECIMAL, nullable=False, default=0)  # 伝票出力区分
    HANM001086 = Column("HANM001086", DECIMAL, nullable=False, default=0)  # 個別設定入力行数
    HANM001087 = Column("HANM001087", CHAR(8), nullable=False)  # 営業所コード
    HANM001088 = Column("HANM001088", CHAR(6), nullable=False)  # 請求グループ
    HANM001089 = Column("HANM001089", DECIMAL, nullable=False, default=0)  # 回収管理単位
    
    # Product code conversion settings
    HANM001090 = Column("HANM001090", DECIMAL, nullable=False, default=0)  # 商品変換コード見積書出力
    HANM001091 = Column("HANM001091", DECIMAL, nullable=False, default=0)  # 商品変換コード売上伝票出力
    HANM001092 = Column("HANM001092", DECIMAL, nullable=False, default=0)  # 商品変換コード請求書出力
    HANM001093 = Column("HANM001093", DECIMAL, nullable=False, default=0)  # 入力処理モード初期値
    
    # Variable text fields
    HANM001K001 = Column("HANM001K001", NVARCHAR(256))  # 納期情報１
    HANM001K002 = Column("HANM001K002", NVARCHAR(256))  # 納期情報２
    HANM001K003 = Column("HANM001K003", NVARCHAR(256))  # 付帯情報区分
    HANM001K004 = Column("HANM001K004", NVARCHAR(256))  # 納品書コメント１
    HANM001K005 = Column("HANM001K005", NVARCHAR(256))  # 納品書コメント２
    HANM001K006 = Column("HANM001K006", NVARCHAR(256))  # 請求書出力順
    HANM001K007 = Column("HANM001K007", NVARCHAR(256))  # 請求書得意先小計区分
    HANM001K008 = Column("HANM001K008", NVARCHAR(256))  # 請求メモ
    HANM001K009 = Column("HANM001K009", NVARCHAR(256))  # 支払条件
    HANM001K010 = Column("HANM001K010", NVARCHAR(256))  # 請求書出力区分
    HANM001K011 = Column("HANM001K011", NVARCHAR(256))  # 請求書控出力区分
    HANM001K012 = Column("HANM001K012", NVARCHAR(256))  # EOS社コード
    HANM001K013 = Column("HANM001K013", NVARCHAR(256))  # EOS店コード
    HANM001K014 = Column("HANM001K014", NVARCHAR(256))  # EOS取引先コード
    HANM001K015 = Column("HANM001K015", NVARCHAR(256))  # 入金後出荷区分
    HANM001K016 = Column("HANM001K016", NVARCHAR(256))  # 請求月区分
    HANM001K017 = Column("HANM001K017", NVARCHAR(256))  # 資料フォルダ
    HANM001K018 = Column("HANM001K018", NVARCHAR(256))  # 経理メールアドレス
    HANM001K019 = Column("HANM001K019", NVARCHAR(256))  # 検索用電話番号
    HANM001K020 = Column("HANM001K020", NVARCHAR(256))  # 拡張項目２０
    
    # Flag and work fields
    HANM001K999 = Column("HANM001K999", DECIMAL, nullable=False, default=0)  # 付箋色番号
    HANM001989 = Column("HANM001989", DECIMAL, nullable=False, default=0)  # 今回請求ワーク－締日付
    HANM001990 = Column("HANM001990", DECIMAL, nullable=False, default=0)  # 今回請求ワーク－入金予定年月日
    HANM001991 = Column("HANM001991", CHAR(6), nullable=False)  # 今回請求ワーク－請求グループ
    HANM001992 = Column("HANM001992", DECIMAL, nullable=False, default=0)  # 今回請求ワーク－請求書番号
    HANM001993 = Column("HANM001993", DECIMAL, nullable=False, default=0)  # 今回請求ワーク－請求処理連番
    HANM001994 = Column("HANM001994", DECIMAL, nullable=False, default=0)  # 今回請求ワーク－消費税自動生成済区分
    HANM001995 = Column("HANM001995", DECIMAL(19, 4), nullable=False, default=0)  # 締日更新ワーク－今回お買上額
    HANM001996 = Column("HANM001996", DECIMAL(19, 4), nullable=False, default=0)  # 締日更新ワーク－今回入金額
    HANM001997 = Column("HANM001997", DECIMAL, nullable=False, default=0)  # 締日更新区分
    HANM001998 = Column("HANM001998", DECIMAL, nullable=False, default=0)  # 年次更新済年
    HANM001999 = Column("HANM001999", DECIMAL, nullable=False, default=0)  # 更新番号
    
    # EB and cost management fields
    HANM001094 = Column("HANM001094", DECIMAL, nullable=False, default=0)  # EB入金手数料－手数料区分
    HANM001095 = Column("HANM001095", DECIMAL, nullable=False, default=0)  # EB入金手数料－算出方法
    HANM001096 = Column("HANM001096", DECIMAL, nullable=False, default=0)  # 原価管理－請求書明細出力順
    HANM001097 = Column("HANM001097", DECIMAL, nullable=False, default=0)  # EB入金－回収消込方法
    
    # Change history
    HANM001901 = Column("HANM001901", CHAR(11), nullable=False)  # 変更履歴－初期得意先コード
    HANM001902 = Column("HANM001902", DECIMAL, nullable=False, default=0)  # 変更履歴－初期得意先コード内連番
    
    # Product display settings
    HANM001098 = Column("HANM001098", DECIMAL, nullable=False, default=0)  # 商品変換CD内訳対応－商品内訳名見積書出力
    HANM001099 = Column("HANM001099", DECIMAL, nullable=False, default=0)  # 商品変換CD内訳対応－商品内訳名売伝票出力
    HANM001100 = Column("HANM001100", DECIMAL, nullable=False, default=0)  # 商品変換CD内訳対応－商品内訳名請求書出力
    
    # Timestamps
    HANM001INS = Column("HANM001INS", DECIMAL(20, 6), nullable=False)  # 登録日時
    HANM001UPD = Column("HANM001UPD", DECIMAL(20, 6), nullable=False)  # 更新日時
    
    # Effective period
    HANM001101 = Column("HANM001101", DECIMAL, nullable=False, default=0)  # 有効期間－開始日
    HANM001102 = Column("HANM001102", DECIMAL, nullable=False, default=0)  # 有効期間－終了日
    
    # Additional fields (continued)
    HANM001103 = Column("HANM001103", DECIMAL, nullable=False, default=0)  # 検収基準－出荷伝票出力
    HANM001104 = Column("HANM001104", DECIMAL, nullable=False, default=0)  # 商品変換コード出荷伝票出力
    HANM001105 = Column("HANM001105", DECIMAL, nullable=False, default=0)  # 商品内訳名出荷伝票出力
    HANM001106 = Column("HANM001106", DECIMAL, nullable=False, default=0)  # 着荷基準－売上伝票出力既定値
    
    # Recovery settings
    HANM001107 = Column("HANM001107", DECIMAL, nullable=False, default=0)  # 回収設定－複数回収設定区分
    HANM001108 = Column("HANM001108", DECIMAL(19, 4), nullable=False, default=0)  # 回収設定－回収設定切替額
    HANM001109 = Column("HANM001109", DECIMAL, nullable=False, default=0)  # 回収設定１－回収設定区分
    HANM001110 = Column("HANM001110", DECIMAL, nullable=False, default=0)  # 回収設定１－回収設定－区分１
    HANM001111 = Column("HANM001111", DECIMAL, nullable=False, default=0)  # 回収設定１－回収設定－区分２
    HANM001112 = Column("HANM001112", DECIMAL, nullable=False, default=0)  # 回収設定１－回収設定－区分３
    HANM001113 = Column("HANM001113", DECIMAL, nullable=False, default=0)  # 回収設定１－回収設定－区分４
    HANM001114 = Column("HANM001114", DECIMAL, nullable=False, default=0)  # 回収設定１－回収設定－区分５
    HANM001115 = Column("HANM001115", DECIMAL(5, 2), nullable=False, default=0)  # 回収設定１－入金率－区分１
    HANM001116 = Column("HANM001116", DECIMAL(5, 2), nullable=False, default=0)  # 回収設定１－入金率－区分２
    HANM001117 = Column("HANM001117", DECIMAL(5, 2), nullable=False, default=0)  # 回収設定１－入金率－区分３
    HANM001118 = Column("HANM001118", DECIMAL(5, 2), nullable=False, default=0)  # 回収設定１－入金率－区分４
    HANM001119 = Column("HANM001119", DECIMAL(5, 2), nullable=False, default=0)  # 回収設定１－入金率－区分５
    HANM001120 = Column("HANM001120", DECIMAL, nullable=False, default=0)  # 回収設定１－単位額－入金方法１
    HANM001121 = Column("HANM001121", DECIMAL, nullable=False, default=0)  # 回収設定１－単位額－入金方法２
    HANM001122 = Column("HANM001122", DECIMAL(19, 4), nullable=False, default=0)  # 回収設定１－単位額－基準単位額
    HANM001123 = Column("HANM001123", DECIMAL, nullable=False, default=0)  # 回収設定１－基準額－入金方法１
    HANM001124 = Column("HANM001124", DECIMAL, nullable=False, default=0)  # 回収設定１－基準額－入金方法２
    HANM001125 = Column("HANM001125", DECIMAL(19, 4), nullable=False, default=0)  # 回収設定１－基準額－基準額
    HANM001126 = Column("HANM001126", DECIMAL, nullable=False, default=0)  # 回収設定１－基準額－基準判断区分
    
    # Recovery settings 2
    HANM001127 = Column("HANM001127", DECIMAL, nullable=False, default=0)  # 回収設定２－回収設定区分
    HANM001128 = Column("HANM001128", DECIMAL, nullable=False, default=0)  # 回収設定２－回収設定－区分１
    HANM001129 = Column("HANM001129", DECIMAL, nullable=False, default=0)  # 回収設定２－回収設定－区分２
    HANM001130 = Column("HANM001130", DECIMAL, nullable=False, default=0)  # 回収設定２－回収設定－区分３
    HANM001131 = Column("HANM001131", DECIMAL, nullable=False, default=0)  # 回収設定２－回収設定－区分４
    HANM001132 = Column("HANM001132", DECIMAL, nullable=False, default=0)  # 回収設定２－回収設定－区分５
    HANM001133 = Column("HANM001133", DECIMAL(5, 2), nullable=False, default=0)  # 回収設定２－入金率－区分１
    HANM001134 = Column("HANM001134", DECIMAL(5, 2), nullable=False, default=0)  # 回収設定２－入金率－区分２
    HANM001135 = Column("HANM001135", DECIMAL(5, 2), nullable=False, default=0)  # 回収設定２－入金率－区分３
    HANM001136 = Column("HANM001136", DECIMAL(5, 2), nullable=False, default=0)  # 回収設定２－入金率－区分４
    HANM001137 = Column("HANM001137", DECIMAL(5, 2), nullable=False, default=0)  # 回収設定２－入金率－区分５
    HANM001138 = Column("HANM001138", DECIMAL, nullable=False, default=0)  # 回収設定２－単位額－入金方法１
    HANM001139 = Column("HANM001139", DECIMAL, nullable=False, default=0)  # 回収設定２－単位額－入金方法２
    HANM001140 = Column("HANM001140", DECIMAL(19, 4), nullable=False, default=0)  # 回収設定２－単位額－基準単位額
    HANM001141 = Column("HANM001141", DECIMAL, nullable=False, default=0)  # 回収設定２－基準額－入金方法１
    HANM001142 = Column("HANM001142", DECIMAL, nullable=False, default=0)  # 回収設定２－基準額－入金方法２
    HANM001143 = Column("HANM001143", DECIMAL(19, 4), nullable=False, default=0)  # 回収設定２－基準額－基準額
    HANM001144 = Column("HANM001144", DECIMAL, nullable=False, default=0)  # 回収設定２－基準額－基準判断区分
    
    # Foreign currency and inventory
    HANM001145 = Column("HANM001145", CHAR(4), nullable=False)  # 汎用在庫－取引パターン
    HANM001146 = Column("HANM001146", DECIMAL, nullable=False, default=0)  # 外貨管理－外貨取引区分
    HANM001147 = Column("HANM001147", CHAR(3), nullable=False)  # 外貨管理－通貨コード
    HANM001148 = Column("HANM001148", DECIMAL, nullable=False, default=0)  # 外貨管理－初期表示レート種類
    HANM001149 = Column("HANM001149", DECIMAL, nullable=False, default=0)  # 外貨管理－外貨入金サイクル
    
    # Additional fields and identifiers
    HANM001150 = Column("HANM001150", CHAR(13), nullable=False)  # 法人番号
    HANM001151 = Column("HANM001151", DECIMAL, nullable=False, default=0)  # 操作日付－操作日付(年月日)
    HANM001152 = Column("HANM001152", NVARCHAR(64))   # 操作日付－ログインID
    
    # Product name settings
    HANM001153 = Column("HANM001153", DECIMAL, nullable=False, default=0)  # 商品変換CD－商品名１・２見積書出力
    HANM001154 = Column("HANM001154", DECIMAL, nullable=False, default=0)  # 商品変換CD－商品名１・２売上伝票出力
    HANM001155 = Column("HANM001155", DECIMAL, nullable=False, default=0)  # 商品変換CD－商品名１・２請求書出力
    HANM001156 = Column("HANM001156", DECIMAL, nullable=False, default=0)  # 商品変換CD－商品名１・２出荷伝票出力
    HANM001157 = Column("HANM001157", DECIMAL, nullable=False, default=0)  # 支払一括入力回収消込方法
    HANM001158 = Column("HANM001158", CHAR(4), nullable=False)  # 請求書鑑パターン
    
    # Address and logistics related fields
    HANM001A001 = Column("HANM001A001", CHAR(2), nullable=False)  # 都道府県コード
    HANM001A002 = Column("HANM001A002", CHAR(2), nullable=False)  # 運送会社コード
    HANM001A003 = Column("HANM001A003", CHAR(6), nullable=False)  # EOS社コード
    HANM001A004 = Column("HANM001A004", CHAR(6), nullable=False)  # EOS店コード
    HANM001A005 = Column("HANM001A005", CHAR(8), nullable=False)  # EOS取引先コード
    HANM001A006 = Column("HANM001A006", DECIMAL, nullable=False, default=0)  # 仮受注可否区分
    HANM001A007 = Column("HANM001A007", DECIMAL, nullable=False, default=0)  # 運送費計算対象区分
    HANM001A008 = Column("HANM001A008", DECIMAL, nullable=False, default=0)  # 請求書発行区分(正)
    HANM001A009 = Column("HANM001A009", DECIMAL, nullable=False, default=0)  # 請求書発行区分(控)
    HANM001A010 = Column("HANM001A010", DECIMAL, nullable=False, default=0)  # 返信封筒要否区分
    
    # Invoice specific customer information
    HANM001A011 = Column("HANM001A011", NVARCHAR(32))  # 得意先名１(請求書用)
    HANM001A012 = Column("HANM001A012", NVARCHAR(32))  # 得意先名２(請求書用)
    HANM001A013 = Column("HANM001A013", CHAR(10), nullable=False)  # 郵便番号(請求書用)
    HANM001A014 = Column("HANM001A014", NVARCHAR(32))  # 住所１(請求書用)
    HANM001A015 = Column("HANM001A015", NVARCHAR(32))  # 住所２(請求書用)
    HANM001A016 = Column("HANM001A016", NVARCHAR(32))  # 住所３(請求書用)
    HANM001A017 = Column("HANM001A017", CHAR(11), nullable=False)  # 優先納品先コード
    HANM001A018 = Column("HANM001A018", CHAR(12), nullable=False)  # 佐川顧客コード
    HANM001A019 = Column("HANM001A019", CHAR(5), nullable=False)  # JIS住所コード
