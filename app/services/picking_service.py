from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.models.picking import PickingManagement, PickingDetail, PickingWork
from app.models.customer import Customer
from app.models.personal import Personal

def get_pickings(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    filters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Get pickings with customer and staff information
    
    Args:
        db: Database session
        skip: Number of records to skip (pagination)
        limit: Number of records to return
        filters: Optional filters to apply to the query
        
    Returns:
        Dict with pickings (list of pickings) and total count
    """
    # Create the base query joining all needed tables
    query = (
        db.query(
            PickingDetail.HANC016001.label("picking_id"),
            PickingDetail.HANC016002.label("picking_date"),
            PickingDetail.HANC016003.label("picking_time"),
            PickingDetail.HANC016A003.label("customer_code_from"),
            PickingDetail.HANC016A004.label("customer_code_to"),
            PickingDetail.HANC016A001.label("order_no_from"),
            PickingDetail.HANC016A002.label("order_no_to"),
            PickingDetail.HANC016014.label("shipping_date"),
            PickingWork.HANW002014.label("staff_code"),
            Customer.HANM001006.label("customer_short_name"),
            Personal.HANM004003.label("staff_short_name")
        )
        .join(PickingWork, PickingDetail.HANC016001 == PickingWork.HANW002009)
        .outerjoin(Customer, PickingDetail.HANC016A003 == Customer.HANM001003)
        .outerjoin(Personal, PickingWork.HANW002014 == Personal.HANM004001)
    )
    
    # # Apply filters if provided
    if filters:
        filter_conditions = []
        
        if filters.get("picking_id"):
            filter_conditions.append(PickingDetail.HANC016001 == filters["picking_id"])
        
        if filters.get("shipping_date_from") and filters.get("shipping_date_to"):
            filter_conditions.append(and_(
                PickingDetail.HANC016014 >= filters["shipping_date_from"],
                PickingDetail.HANC016014.HANC016024 <= filters["shipping_date_to"]
            ))
        elif filters.get("shipping_date_from"):
            filter_conditions.append(PickingDetail.HANC016014 >= filters["shipping_date_from"])
        elif filters.get("shipping_date_to"):
            filter_conditions.append(PickingDetail.HANC016014 <= filters["shipping_date_to"])
        
        if filters.get("customer_code"):
            filter_conditions.append(or_(
                PickingDetail.HANC016A003 == filters["customer_code"],
                PickingDetail.HANC016A004 == filters["customer_code"]
            ))
            
        if filters.get("staff_code"):
            filter_conditions.append(PickingWork.HANW002014 == filters["staff_code"])
        
        if filter_conditions:
            query = query.filter(and_(*filter_conditions))
    
    # Get total count
    total = query.count()
    # Apply pagination
    query = query.order_by(desc(PickingDetail.HANC016001)).offset(skip).limit(limit)
    
    # Execute query
    result = query.all()
    
    # Format the results
    pickings = []
    for row in result:
        pickings.append({
            "picking_id": row.picking_id,
            "picking_date": row.picking_date,
            "picking_time": row.picking_time,
            "shipping_date": row.shipping_date,
            "order_no_from": str(row.order_no_from),
            "order_no_to": str(row.order_no_to),
            "customer_code_from": row.customer_code_from.strip(),
            "customer_code_to": row.customer_code_to.strip(),
            "customer_short_name": row.customer_short_name.strip() if row.customer_short_name else "",
            "staff_code": row.staff_code.strip(),
            "staff_short_name": row.staff_short_name.strip() if row.staff_short_name else ""
        })

    return {
        "pickings": pickings,
        "total": total
    } 