from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.db.base import get_db
from app.schemas.picking import PickingRead, PickingList
from app.services import picking_service

router = APIRouter()

@router.get("/", response_model=PickingList)
def read_pickings(
    skip: int = 0, 
    limit: int = 100,
    picking_id: Optional[int] = None,
    shipping_date_from: Optional[str] = None,
    shipping_date_to: Optional[str] = None,
    customer_code: Optional[str] = None,
    staff_code: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve pickings with pagination and optional filtering.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Number of records to return per page
    - **picking_id**: Filter by picking ID
    - **shipping_date_from**: Filter by shipping date >= (format: YYYYMMDD)
    - **shipping_date_to**: Filter by shipping date <= (format: YYYYMMDD)
    - **customer_code**: Filter by customer code
    - **staff_code**: Filter by staff code
    """
    filters = {}
    
    if picking_id is not None:
        filters["picking_id"] = picking_id
    
    if shipping_date_from:
        filters["shipping_date_from"] = shipping_date_from
    
    if shipping_date_to:
        filters["shipping_date_to"] = shipping_date_to
    
    if customer_code:
        filters["customer_code"] = customer_code
    
    if staff_code:
        filters["staff_code"] = staff_code
    
    result = picking_service.get_pickings(db, skip=skip, limit=limit, filters=filters)
    
    return {
        "pickings": result["pickings"],
        "total": result["total"],
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit
    }