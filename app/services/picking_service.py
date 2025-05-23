import os
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import Optional, Dict, Any

from app.core.config import settings

from app.models.picking import PickingManagement, PickingDetail, PickingWork
from app.models.customer import Customer
from app.models.personal import Personal
from app.models.juhachu import JuHachuHeader

def get_pickings(
    db: Session,
    skip: int = 0,
    limit: int = 50,
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
            Personal.HANM004001.label("staff_code"),
            Customer.HANM001006.label("customer_short_name"),
            Personal.HANM004003.label("staff_short_name"),
            func.count(JuHachuHeader.HANR004005).label("order_count")
        )
        .join(PickingManagement, PickingDetail.HANC016001 == PickingManagement.HANCA11001)
        .join(Customer, PickingDetail.HANC016A003 == Customer.HANM001003)
        .outerjoin(Personal, Customer.HANM001015 == Personal.HANM004001)
        .join(PickingWork, PickingDetail.HANC016001 == PickingWork.HANW002009)
        .join(
            JuHachuHeader,
            and_(
                JuHachuHeader.HANR004004 == PickingWork.HANW002001,
                JuHachuHeader.HANR004005 == PickingWork.HANW002002
            )
        )
    )

    # Carrier code exclusion logic
    if not settings.ENV == "Development":
        query = query.filter(
            PickingManagement.HANCA11002 == 0,
                PickingWork.HANW002A003 == settings.CARRIER_UNASSIGNED_CODE
        )

    query = query.group_by(
        PickingDetail.HANC016001,
        PickingDetail.HANC016002,
        PickingDetail.HANC016003,
        PickingDetail.HANC016A003,
        PickingDetail.HANC016A004,
        PickingDetail.HANC016A001,
        PickingDetail.HANC016A002,
        PickingDetail.HANC016014,
        Personal.HANM004001,
        Customer.HANM001006,
        Personal.HANM004003
    )

    # Apply filters if provided
    if filters:
        filter_conditions = []

        if filters.get("query"):
            filter_conditions.append(or_(
                Customer.HANM001006.like(f"%{filters['query']}%"),
                Personal.HANM004003.like(f"%{filters['query']}%"),
                PickingDetail.HANC016001.like(f"%{filters['query']}%"),
                PickingDetail.HANC016A003.like(f"%{filters['query']}%"),
                PickingDetail.HANC016003.like(f"%{filters['query']}%"),
                PickingDetail.HANC016A004.like(f"%{filters['query']}%"),
                PickingDetail.HANC016A001.like(f"%{filters['query']}%"),
                PickingDetail.HANC016A002.like(f"%{filters['query']}%")
            ))

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
            "staff_code": row.staff_code,
            "staff_short_name": row.staff_short_name.strip() if row.staff_short_name else "",
            "order_count": row.order_count
        })

    return {
        "pickings": pickings,
        "total": total
    }
