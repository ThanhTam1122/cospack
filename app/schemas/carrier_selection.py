from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date


class ProductInfo(BaseModel):
    """Product information for calculating shipping volume and weight"""
    product_code: int
    quantity: int
    set_quantity: int = 1  # 入数 - how many items in one box
    set_parcel_count: int = 1  # セット個口数量 - how many parcels per set
    outer_box_count: int = 1  # 外箱入数 - capacity of outer box
    weight_per_unit: float  # Weight per unit in kg
    outer_box_dimensions: Dict[str, float] = Field(
        ..., 
        description="Dimensions of outer box in cm",
        example={"length": 30, "width": 20, "height": 15}
    )


class CarrierEstimate(BaseModel):
    """Estimated shipping cost for a specific carrier"""
    carrier_code: str
    carrier_name: str
    parcel_count: int
    volume: float  # 才数 - volume unit (1 unit = 30.3cm cube)
    weight: float  # Weight in kg
    size: float  # Sum of three sides in cm
    cost: float  # Shipping cost
    lead_time: int  # Delivery lead time in days
    is_capacity_available: bool  # Whether carrier has capacity for this shipment


class CarrierSelectionRequest(BaseModel):
    """Request for carrier selection"""
    picking_id: int
    delivery_postal_code: Optional[str] = None
    jis_address_code: Optional[str] = None
    shipping_date: Optional[date] = None
    delivery_date: Optional[date] = None
    products: Optional[List[ProductInfo]] = None


class CarrierSelectionDetail(BaseModel):
    """Detailed information about a carrier selection"""
    parcel_count: int
    volume: float
    weight: float
    size: float
    carrier_estimates: List[CarrierEstimate]
    selected_carrier_code: str
    selected_carrier_name: str
    selection_reason: str


class CarrierSelectionResponse(BaseModel):
    """Response for carrier selection"""
    picking_id: int
    waybill_count: int
    selection_details: List[CarrierSelectionDetail]
    success: bool
    message: Optional[str] = None


class CarrierSelectionBatchRequest(BaseModel):
    """Request for batch carrier selection"""
    picking_ids: List[int]


class CarrierSelectionBatchResponse(BaseModel):
    """Response for batch carrier selection"""
    results: List[CarrierSelectionResponse]
    success: bool
    message: Optional[str] = None
    failed_pickings: Optional[List[int]] = None 