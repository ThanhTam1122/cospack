from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.db.base import get_db
from app.schemas.carrier_selection import (
    CarrierSelectionRequest,
    CarrierSelectionResponse,
    CarrierSelectionBatchRequest,
    CarrierSelectionBatchResponse
)
from app.services import carrier_selection_service

# Setup logger
logger = logging.getLogger(__name__)

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
    try:
        result = carrier_selection_service.select_carriers_for_picking(db, request.picking_id)
        return result
    except Exception as e:
        logger.error(f"Error selecting carrier: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error selecting carrier: {str(e)}")

@router.post("/batch-select", response_model=CarrierSelectionBatchResponse)
def batch_select_carriers(
    request: CarrierSelectionBatchRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Process carrier selection for multiple pickings in batch
    
    This endpoint processes multiple pickings and selects the optimal carrier for each waybill
    in each picking based on shipping metrics, carrier capacity, and cost.
    
    For large batches, processing happens in the background and returns immediately.
    """
    # If batch is small, process immediately
    if len(request.picking_ids) <= 10:
        try:
            result = carrier_selection_service.batch_select_carriers(db, request.picking_ids)
            return result
        except Exception as e:
            logger.error(f"Error processing batch carrier selection: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error processing batch: {str(e)}")
    
    # For larger batches, process in background
    background_tasks.add_task(
        carrier_selection_service.batch_select_carriers,
        db,
        request.picking_ids
    )
    
    return {
        "results": [],
        "success": True,
        "message": f"Processing {len(request.picking_ids)} pickings in background"
    }

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
    try:
        result = carrier_selection_service.select_carriers_for_picking(db, picking_id)
        return result
    except Exception as e:
        logger.error(f"Error retrieving carrier selection: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving carrier selection: {str(e)}")