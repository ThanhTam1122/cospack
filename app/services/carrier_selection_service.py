from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from typing import List, Optional, Dict, Any, Tuple
from datetime import date, datetime
import math
import requests
import logging

from app.models.picking import PickingManagement, PickingDetail, PickingWork
from app.models.customer import Customer
from app.models.personal import Personal
from app.models.transportation_area import TransportationArea
from app.models.transportation_area_jis import TransportationAreaJISMapping
from app.models.transportation_fee import TransportationFee
from app.models.transportation_capacity import TransportationCapacity
from app.models.shipping_slip import ShippingSlip
from app.models.carrier_selection_log import CarrierSelectionLog
from app.models.carrier_selection_log_detail import CarrierSelectionLogDetail
from app.models.product_master import ProductMaster
from app.models.product_sub_master import ProductSubMaster
from app.models.holiday_calendar_master import HolidayCalendarMaster
from app.models.special_lead_time_master import SpecialLeadTimeMaster
from app.models.transportation_company_master import TransportationCompanyMaster

from app.services.fee_calculation_service import FeeCalculationService

# Setup logger
logger = logging.getLogger(__name__)

# Constants
VOLUME_CUBE_SIZE = 30.3  # cm
VOLUME_TO_WEIGHT_RATIO = 8  # 1 volume (30.3cm cube) = 8kg
POSTCODE_API_KEY = "__apikey__"  # Replace with actual API key

class CarrierSelectionService:
    def __init__(self, db: Session):
        self.db = db
        self.fee_calculator = FeeCalculationService(db)
    
    def get_jis_code_from_postal_code(self, postal_code: str) -> Optional[str]:
        """
        Get JIS address code from postal code using PostcodeJP API
        """
        try:
            # Remove any hyphens or spaces
            postal_code = postal_code.replace("-", "").replace(" ", "")
            
            # Make API request
            url = f"https://postcode-jp.com/api/postcode/{postal_code}"
            headers = {"apikey": POSTCODE_API_KEY}
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data and "data" in data and len(data["data"]) > 0:
                    address = data["data"][0]
                    # Extract city and prefecture codes
                    prefecture_code = address.get("prefecture_code", "")
                    city_code = address.get("city_code", "")
                    
                    if prefecture_code and city_code:
                        # Combine to create 5-digit JIS code
                        return f"{prefecture_code}{city_code}"
            
            logger.warning(f"Could not find JIS code for postal code {postal_code}")
            return None
        
        except Exception as e:
            logger.error(f"Error fetching JIS code for postal code {postal_code}: {str(e)}")
            return None

    def get_area_code_from_jis_code(self, jis_code: str) -> Optional[int]:
        """
        Get transportation area code from JIS address code
        """
        mapping = self.db.query(TransportationAreaJISMapping).filter(
            TransportationAreaJISMapping.HANM007002 == jis_code
        ).first()
        
        if mapping:
            return mapping.HANM007001
        
        logger.warning(f"Could not find transportation area for JIS code {jis_code}")
        return None

    def calculate_package_metrics(self, products: List[Dict[str, Any]]) -> Tuple[int, float, float, int]:
        """
        Calculate package metrics based on products
        
        Returns:
            Tuple containing (parcel_count, volume, weight, size)
        """
        # Use the fee calculator service to get detailed product metrics
        return self.fee_calculator.calculate_package_metrics(products)

    def calculate_shipping_fee(self, carrier_code: str, area_code: int, 
                             parcels: int, volume: float, weight: float, size: float) -> Optional[float]:
        """
        Calculate shipping fee based on carrier, area, and package metrics
        """
        # Use the fee calculator service to calculate shipping fee
        return self.fee_calculator.calculate_shipping_fee(
            carrier_code=carrier_code,
            area_code=area_code,
            parcels=parcels,
            volume=volume,
            weight=weight,
            size=size
        )

    def check_carrier_capacity(self, carrier_code: str, volume: float, weight: float) -> bool:
        """
        Check if the carrier has enough capacity for this shipment
        """
        # Use the fee calculator service to check carrier capacity
        return self.fee_calculator.check_carrier_capacity(
            carrier_code=carrier_code,
            volume=volume,
            weight=weight
        )

    def calculate_lead_time(self, carrier_code: str, prefecture_code: str, 
                          shipping_date: date) -> Optional[int]:
        """
        Calculate lead time based on carrier, prefecture, and shipping date
        """
        # Use the fee calculator service to calculate lead time
        return self.fee_calculator.calculate_lead_time(
            carrier_code=carrier_code,
            prefecture_code=prefecture_code,
            shipping_date=shipping_date
        )

    def select_optimal_carrier(self, area_code: int, parcels: int, volume: float, 
                             weight: float, size: float, shipping_date: date, 
                             delivery_date: date, jis_code: str = None) -> Dict[str, Any]:
        """
        Select the optimal carrier based on shipping metrics and other factors
        
        Returns:
            Dict with carrier selection details
        """
        # If JIS code is provided, use it directly with the fee calculator
        if jis_code:
            result = self.fee_calculator.select_optimal_carrier(
                jis_code=jis_code,
                parcels=parcels,
                volume=volume,
                weight=weight,
                size=size,
                shipping_date=shipping_date
            )
            return result
        
        # Otherwise, use the traditional approach with area code
        # Get all available carriers
        carriers = self.db.query(TransportationCompanyMaster).all()
        
        estimates = []
        cheapest_carrier = None
        cheapest_cost = float('inf')
        
        for carrier in carriers:
            carrier_code = carrier.HANMA02001
            carrier_name = carrier.HANMA02002
            
            # Check if carrier has capacity
            has_capacity = self.check_carrier_capacity(carrier_code, volume, weight)
            
            # Calculate shipping fee
            fee = self.calculate_shipping_fee(carrier_code, area_code, parcels, volume, weight, size)
            
            # Calculate lead time
            prefecture_code = "13"  # Default to Tokyo if we don't have JIS code
            lead_time = self.calculate_lead_time(carrier_code, prefecture_code, shipping_date)
            
            # Skip carriers with no fee information
            if fee is None or lead_time is None:
                continue
                
            # Create carrier estimate
            estimate = {
                "carrier_code": carrier_code,
                "carrier_name": carrier_name,
                "parcel_count": parcels,
                "volume": volume,
                "weight": weight,
                "size": size,
                "cost": fee,
                "lead_time": lead_time,
                "is_capacity_available": has_capacity
            }
            
            estimates.append(estimate)
            
            # Track cheapest carrier
            if fee < cheapest_cost and has_capacity:
                cheapest_cost = fee
                cheapest_carrier = estimate
        
        # Select a carrier based on business rules
        # In this simple example, we just choose the cheapest carrier
        # In a real system, you would consider lead time, previous carrier usage, etc.
        selected_carrier = cheapest_carrier
        selection_reason = "Lowest cost carrier"
        
        if not selected_carrier:
            return {
                "success": False,
                "message": "No suitable carrier found",
                "carriers": estimates
            }
        
        return {
            "success": True,
            "carriers": estimates,
            "selected_carrier": selected_carrier,
            "selection_reason": selection_reason
        }

    def save_carrier_selection_log(self, waybill_id: int, parcel_count: int, 
                                 volume: float, weight: float, selected_carrier: int,
                                 cheapest_carrier: int, reason: str,
                                 products: List[Dict[str, Any]] = None) -> int:
        """
        Save the carrier selection to the log table
        
        Returns:
            The log ID
        """
        # Create log entry
        log = CarrierSelectionLog(
            HANM010002=waybill_id,
            HANM010003=parcel_count,
            HANM010004=int(volume),
            HANM010005=int(weight),
            HANM010006=cheapest_carrier,
            HANM010007=selected_carrier,
            HANM010008=reason
        )
        
        self.db.add(log)
        self.db.flush()  # To get the ID
        
        # Add product details if provided
        if products and log.HANM010001:
            for product in products:
                product_code = product["product_code"]
                size = (
                    product["outer_box_dimensions"]["length"] + 
                    product["outer_box_dimensions"]["width"] + 
                    product["outer_box_dimensions"]["height"]
                )
                
                detail = CarrierSelectionLogDetail(
                    HANM011001=log.HANM010001,
                    HANM011002=product_code,
                    HANM011003=int(size),
                    HANM011004=math.ceil(product["quantity"] * product.get("set_quantity", 1) / product["outer_box_count"])
                    if product["outer_box_count"] > 0 else 1
                )
                
                self.db.add(detail)
        
        return log.HANM010001 if log.HANM010001 else 0

    def update_smilev_database(self, waybill_id: int, carrier_code: int) -> bool:
        """
        Update SmileV database with selected carrier
        This is a placeholder - actual implementation would depend on SmileV API
        """
        try:
            # Update shipping slip with selected carrier
            shipping_slip = self.db.query(ShippingSlip).filter(
                ShippingSlip.HANM009001 == waybill_id
            ).first()
            
            if shipping_slip:
                # Update carrier code (assuming field exists)
                # shipping_slip.carrier_code = carrier_code
                # self.db.commit()
                
                # For now, just log the action
                logger.info(f"Would update SmileV: Waybill {waybill_id} assigned to carrier {carrier_code}")
                return True
            else:
                logger.warning(f"Shipping slip {waybill_id} not found for SmileV update")
                return False
                
        except Exception as e:
            logger.error(f"Error updating SmileV database: {str(e)}")
            return False

    def get_picking_waybills(self, picking_id: int) -> List[Dict[str, Any]]:
        """
        Group picking data into waybills based on delivery destination, date, etc.
        
        Returns:
            List of waybill data dictionaries
        """
        # Get all picking detail records for this picking ID
        picking_details = self.db.query(PickingDetail).filter(
            PickingDetail.HANC016001 == picking_id
        ).all()
        
        if not picking_details:
            logger.warning(f"No picking details found for picking ID {picking_id}")
            return []
        
        # Group by delivery destination, shipping date, and delivery date
        waybills = {}
        
        for detail in picking_details:
            # Extract grouping keys
            customer_code = detail.HANC016A003.strip() if detail.HANC016A003 else ""
            shipping_date = detail.HANC016014
            # Assuming delivery date is stored somewhere
            delivery_date = detail.HANC016024 if hasattr(detail, 'HANC016024') else shipping_date
            
            # Create group key
            group_key = f"{customer_code}_{shipping_date}_{delivery_date}"
            
            # Get customer for JIS code
            customer = self.db.query(Customer).filter(
                Customer.HANM001003 == customer_code
            ).first()
            
            jis_code = customer.HANM001A019.strip() if customer and customer.HANM001A019 else None
            postal_code = customer.HANM001008.strip() if customer and customer.HANM001008 else None
            
            # Create or update group
            if group_key not in waybills:
                # Convert dates from YYYYMMDD format
                shipping_date_str = str(shipping_date)
                delivery_date_str = str(delivery_date)
                
                shipping_date_obj = date(
                    int(shipping_date_str[0:4]),
                    int(shipping_date_str[4:6]),
                    int(shipping_date_str[6:8])
                ) if len(shipping_date_str) >= 8 else date.today()
                
                delivery_date_obj = date(
                    int(delivery_date_str[0:4]),
                    int(delivery_date_str[4:6]),
                    int(delivery_date_str[6:8])
                ) if len(delivery_date_str) >= 8 else shipping_date_obj
                
                waybills[group_key] = {
                    "waybill_id": len(waybills) + 1,  # Temporary ID
                    "customer_code": customer_code,
                    "jis_code": jis_code,
                    "postal_code": postal_code,
                    "shipping_date": shipping_date_obj,
                    "delivery_date": delivery_date_obj,
                    "products": []
                }
            
            # Get actual product data instead of placeholders
            product_code = detail.HANC016004  # Product code from picking detail
            quantity = detail.HANC016005 or 1  # Quantity from picking detail
            
            # Get detailed product info using fee calculator service
            product_info = self.fee_calculator.get_product_info(product_code)
            
            if product_info:
                # Add product to this waybill with real data
                waybills[group_key]["products"].append({
                    "product_code": product_code,
                    "quantity": quantity,
                    "set_quantity": product_info.get("set_quantity", 1),
                    "outer_box_count": product_info.get("outer_box_count", 1),
                    "weight_per_unit": product_info.get("weight_per_unit", 0),
                    "outer_box_dimensions": product_info.get("outer_box_dimensions", {
                        "length": 0,
                        "width": 0,
                        "height": 0
                    })
                })
            else:
                # If product info not found, use default values
                logger.warning(f"Product info not found for code {product_code}, using defaults")
                waybills[group_key]["products"].append({
                    "product_code": product_code,
                    "quantity": quantity,
                    "set_quantity": 1,
                    "outer_box_count": 1,
                    "weight_per_unit": 1.0,
                    "outer_box_dimensions": {
                        "length": 30,
                        "width": 20,
                        "height": 15
                    }
                })
        
        return list(waybills.values())

    def select_carriers_for_picking(self, picking_id: int) -> Dict[str, Any]:
        """
        Select optimal carriers for all waybills in a picking
        
        Returns:
            Selection results
        """
        waybills = self.get_picking_waybills(picking_id)
        
        if not waybills:
            return {
                "picking_id": picking_id,
                "waybill_count": 0,
                "selection_details": [],
                "success": False,
                "message": f"No waybills found for picking ID {picking_id}"
            }
        
        selection_details = []
        
        for waybill in waybills:
            # Get area code from JIS code
            area_code = None
            if waybill.get("jis_code"):
                area_code = self.get_area_code_from_jis_code(waybill["jis_code"])
            elif waybill.get("postal_code"):
                jis_code = self.get_jis_code_from_postal_code(waybill["postal_code"])
                if jis_code:
                    area_code = self.get_area_code_from_jis_code(jis_code)
            
            if not area_code:
                logger.warning(f"Could not determine area code for waybill {waybill['waybill_id']}")
                continue
            
            # Calculate package metrics
            parcels, volume, weight, size = self.calculate_package_metrics(waybill["products"])
            
            # Select optimal carrier
            carrier_selection = self.select_optimal_carrier(
                area_code=area_code,
                parcels=parcels,
                volume=volume,
                weight=weight,
                size=size,
                shipping_date=waybill["shipping_date"],
                delivery_date=waybill["delivery_date"],
                jis_code=waybill.get("jis_code")
            )
            
            # Save to log
            if carrier_selection["selected_carrier"]:
                cheapest_carrier = min(carrier_selection["carriers"], 
                                     key=lambda x: x["cost"])["carrier_code"] if carrier_selection["carriers"] else None
                
                log_id = self.save_carrier_selection_log(
                    waybill_id=waybill["waybill_id"],
                    parcel_count=parcels,
                    volume=volume,
                    weight=weight,
                    selected_carrier=carrier_selection["selected_carrier"]["carrier_code"],
                    cheapest_carrier=cheapest_carrier if cheapest_carrier else carrier_selection["selected_carrier"]["carrier_code"],
                    reason=carrier_selection["selection_reason"],
                    products=waybill["products"]
                )
                
                # Update SmileV database
                self.update_smilev_database(
                    waybill_id=waybill["waybill_id"],
                    carrier_code=carrier_selection["selected_carrier"]["carrier_code"]
                )
            
            # Add to results
            selection_details.append({
                "waybill_id": waybill["waybill_id"],
                "parcel_count": parcels,
                "volume": volume,
                "weight": weight,
                "size": size,
                "carriers": carrier_selection["carriers"],
                "selected_carrier_code": carrier_selection["selected_carrier"]["carrier_code"],
                "selected_carrier_name": carrier_selection["selected_carrier"]["carrier_name"],
                "selection_reason": carrier_selection["selection_reason"]
            })
        
        return {
            "picking_id": picking_id,
            "waybill_count": len(waybills),
            "selection_details": selection_details,
            "success": True,
            "message": f"Carrier selection completed for {len(selection_details)} waybills"
        }

    def batch_select_carriers(self, picking_ids: List[int]) -> Dict[str, Any]:
        """
        Process multiple pickings in batch
        
        Returns:
            Batch selection results
        """
        results = []
        success_count = 0
        
        for picking_id in picking_ids:
            result = self.select_carriers_for_picking(picking_id)
            results.append(result)
            
            if result["success"]:
                success_count += 1
        
        return {
            "results": results,
            "success": success_count > 0,
            "message": f"Processed {len(picking_ids)} pickings, {success_count} successful"
        }


def select_carriers_for_picking(db: Session, picking_id: int) -> Dict[str, Any]:
    """
    Select optimal carriers for all waybills in a picking
    
    Args:
        db: Database session
        picking_id: Picking ID
        
    Returns:
        Selection results
    """
    service = CarrierSelectionService(db)
    return service.select_carriers_for_picking(picking_id)


def batch_select_carriers(db: Session, picking_ids: List[int]) -> Dict[str, Any]:
    """
    Process multiple pickings in batch
    
    Args:
        db: Database session
        picking_ids: List of picking IDs
        
    Returns:
        Batch selection results
    """
    service = CarrierSelectionService(db)
    return service.batch_select_carriers(picking_ids) 