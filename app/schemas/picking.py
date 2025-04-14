from pydantic import BaseModel
from typing import List
from datetime import datetime

class PickingRead(BaseModel):
    """Schema for reading picking data with required fields for UI table"""
    picking_id: int  # ピッキング連番
    picking_date: datetime  # ピッキング日
    picking_time: datetime  # ピッキング時刻
    shipping_date: datetime  # 出荷日付
    order_no_from: str  # 受注No_From
    order_no_to: str  # 受注No_To
    customer_code_from: str  # 得意先CD_From
    customer_code_to: str  # 得意先CD_To
    customer_short_name: str  # 得意先略称
    staff_code: str  # 担当者CD
    staff_short_name: str  # 担当者略称

class PickingList(BaseModel):
    """Paged response of picking data for UI table"""
    pickings: List[PickingRead]
    total: int
    page: int
    size: int 