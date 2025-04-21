from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date


class ProductInfo(BaseModel):
    """Product information for calculating shipping volume and weight"""
    product_code: int
    quantity: int
    set_quantity: int = 1
    outer_box_count: int
    weight_per_unit: float
    outer_box_dimensions: Dict[str, float] = Field(
        ..., 
        description="Dimensions of outer box in cm",
        example={"length": 30, "width": 20, "height": 15}
    )


class CarrierEstimate(BaseModel):
    """Estimated shipping cost for a specific carrier"""
    carrier_code: int
    carrier_name: str
    parcel_count: int
    volume: float
    weight: float
    size: int
    cost: float
    lead_time: int
    is_capacity_available: bool


class CarrierSelectionRequest(BaseModel):
    """Request for carrier selection"""
    picking_id: int
    delivery_postal_code: Optional[str] = None
    jis_address_code: Optional[str] = None
    shipping_date: date
    delivery_date: date
    products: List[ProductInfo]


class CarrierSelectionDetail(BaseModel):
    """Detailed information about a carrier selection"""
    waybill_id: int
    parcel_count: int
    volume: float
    weight: float
    size: int
    carrier_estimates: List[CarrierEstimate]
    selected_carrier_code: int
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