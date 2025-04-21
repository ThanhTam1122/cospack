from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.db.base import get_db
from app.schemas.carrier_selection import (
    CarrierSelectionRequest,
    CarrierSelectionResponse,
    CarrierSelectionBatchRequest,
    CarrierSelectionBatchResponse
)
from app.services import carrier_selection_service

router = APIRouter()

@router.post("/select", response_model=CarrierSelectionResponse)
def select_carrier(
    request: CarrierSelectionRequest,
    db: Session = Depends(get_db)
):
    """
    Select optimal carrier for a picking
    
    This endpoint processes a single picking and selects the optimal carrier for each waybill
    based on shipping metrics, carrier capacity, and cost.
    """
    result = carrier_selection_service.select_carriers_for_picking(db, request.picking_id)
    
    return result

@router.post("/batch-select", response_model=CarrierSelectionBatchResponse)
def batch_select_carriers(
    request: CarrierSelectionBatchRequest,
    db: Session = Depends(get_db)
):
    """
    Process carrier selection for multiple pickings in batch
    
    This endpoint processes multiple pickings and selects the optimal carrier for each waybill
    in each picking based on shipping metrics, carrier capacity, and cost.
    """
    result = carrier_selection_service.batch_select_carriers(db, request.picking_ids)
    
    return result

@router.get("/{picking_id}", response_model=CarrierSelectionResponse)
def get_carrier_selection(
    picking_id: int,
    db: Session = Depends(get_db)
):
    """
    Get carrier selection results for a picking
    
    This endpoint retrieves the results of carrier selection for a specific picking.
    If carrier selection has not been performed, it will be executed.
    """
    result = carrier_selection_service.select_carriers_for_picking(db, picking_id)
    
    return result 