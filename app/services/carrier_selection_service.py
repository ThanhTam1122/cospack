from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from typing import List, Optional, Dict, Any, Tuple
from datetime import date, datetime, timedelta
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
from app.models.carrier_selection_log import CarrierSelectionLog
from app.models.carrier_selection_log_detail import CarrierSelectionLogDetail
from app.models.product_master import ProductMaster
from app.models.product_sub_master import ProductSubMaster
from app.models.holiday_calendar_master import HolidayCalendarMaster
from app.models.special_lead_time_master import SpecialLeadTimeMaster
from app.models.transportation_company_master import TransportationCompanyMaster
from app.models.juhachu import JuHachuHeader, MeisaiKakucho
from app.models.waybill import Waybill
from app.models.special_capacity import SpecialCapacity

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

    def calculate_package_metrics(self, products: List[Dict[str, Any]]) -> Tuple[int, float, float, float, List[Dict[str, Any]]]:
        """
        Calculate package metrics based on products
        
        Returns:
            Tuple containing (parcel_count, volume, weight, size, parcels_info)
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
                                 volume: float, weight: float, size: float,
                                 selected_carrier: str, cheapest_carrier: str, 
                                 reason: str, all_carriers: List[Dict[str, Any]],
                                 products: List[Dict[str, Any]] = None) -> int:
        """
        Save the carrier selection to the log table
        
        Returns:
            The log ID
        """
        # Create log entry
        log = CarrierSelectionLog(
            HANM010002=waybill_id,                # Waybill ID
            HANM010003=parcel_count,              # Parcel count
            HANM010004=int(volume),               # Volume (才数)
            HANM010005=int(weight),               # Weight (重量)
            HANM010006=size,                      # Size (サイズ)
            HANM010007=cheapest_carrier,          # Cheapest carrier
            HANM010008=selected_carrier,          # Selected carrier 
            HANM010009=reason                     # Selection reason
        )
        
        self.db.add(log)
        self.db.flush()  # To get the ID
        
        # Add carrier estimate details
        if log.HANM010001 and all_carriers:
            for idx, carrier in enumerate(all_carriers):
                carrier_detail = CarrierSelectionLogDetail(
                    HANM011001=log.HANM010001,                # Log ID
                    HANM011002=carrier["carrier_code"],       # Carrier code
                    HANM011003=carrier["cost"],               # Estimated cost
                    HANM011004=carrier["lead_time"],          # Lead time
                    HANM011005=carrier["is_capacity_available"] # Capacity available
                )
                self.db.add(carrier_detail)
        
        # Add product details if provided
        if products and log.HANM010001:
            for product in products:
                product_code = product["product_code"]
                dimensions = product.get("outer_box_dimensions", {})
                size = (
                    dimensions.get("length", 0) + 
                    dimensions.get("width", 0) + 
                    dimensions.get("height", 0)
                )
                
                outer_box_count = product.get("outer_box_count", 1) or 1
                quantity = product.get("quantity", 0) or 0
                set_quantity = product.get("set_quantity", 1) or 1
                
                box_count = math.ceil(quantity * set_quantity / outer_box_count)
                
                detail = CarrierSelectionLogDetail(
                    HANM011001=log.HANM010001,       # Log ID
                    HANM011002=product_code,         # Product code
                    HANM011003=int(size),            # Size
                    HANM011004=box_count             # Box count
                )
                
                self.db.add(detail)
        
        return log.HANM010001 if log.HANM010001 else 0

    def update_database(self, waybill_id: str, carrier_code: str) -> None:
        """
        Update the database with the selected carrier for a waybill
        
        Args:
            waybill_id: The ID of the waybill
            carrier_code: The code of the selected transportation company
        """
        # Check if there is already a carrier assignment for this waybill
        existing = self.db.query(WaybillToCarrier).filter(
            WaybillToCarrier.HANPK04001 == waybill_id
        ).first()
        
        if existing:
            # Update existing record
            existing.HANPK04002 = carrier_code
            existing.HANPK04UPD = datetime.now()
        else:
            # Create new record
            new_record = WaybillToCarrier(
                HANPK04001=waybill_id,
                HANPK04002=carrier_code,
                HANPK04REG=datetime.now(),
                HANPK04UPD=datetime.now()
            )
            self.db.add(new_record)
        
        # Commit the transaction
        self.db.commit()

    def update_smilev_database(self, waybill_id: str, carrier_code: str) -> None:
        """
        Update the SmileV database with the selected carrier for a waybill
        
        Args:
            waybill_id: The ID of the waybill
            carrier_code: The code of the selected transportation company
        """
        # Implementation for external SmileV database update
        # This would typically involve API calls or direct database connection
        # For now, we just log the action
        logger.info(f"Would update SmileV database: waybill {waybill_id} assigned to carrier {carrier_code}")
        
    def update_special_capacity(self, carrier_code: str, prefecture_code: str, shipping_date: date) -> None:
        """
        Update the special capacity record when a carrier is selected
        
        Args:
            carrier_code: Transportation company code
            prefecture_code: Prefecture code
            shipping_date: Shipping date
        """
        # Convert date to YYYYMMDD format without hyphens
        shipping_date_str = shipping_date.strftime('%Y%m%d')
        
        # Find the special capacity record
        special_capacity = self.db.query(SpecialCapacity).filter(
            SpecialCapacity.HANMA15001 == carrier_code,
            SpecialCapacity.HANMA15002 == prefecture_code,
            SpecialCapacity.HANMA15003 == shipping_date_str
        ).first()
        
        if special_capacity and special_capacity.HANMA15005 > 0:
            # Decrement the remaining cases count
            special_capacity.HANMA15005 -= 1
            special_capacity.HANMA15UPD = datetime.now()
            self.db.commit()
            logger.info(f"Updated special capacity for carrier {carrier_code}, prefecture {prefecture_code}, date {shipping_date_str}. Remaining: {special_capacity.HANMA15005}")
            
    def get_picking_waybills(self, picking_id: str) -> List[Dict[str, Any]]:
        """
        Get all waybills for a picking with their shipping details
        
        Args:
            picking_id: The ID of the picking
            
        Returns:
            List of waybills with their shipping details
        """
        waybills = self.db.query(Waybill).filter(
            Waybill.HANPK02003 == picking_id
        ).all()
        
        result = []
        for waybill in waybills:
            waybill_data = {
                "waybill_id": waybill.HANPK02001,
                "customer_id": waybill.HANPK02002,
                "shipping_date": waybill.HANPK02005,
                "delivery_deadline": waybill.HANPK02006,
                "jis_code": waybill.HANPK02007,
                "parcels": waybill.HANPK02008,
                "volume": waybill.HANPK02009,
                "weight": waybill.HANPK02010,
                "size": waybill.HANPK02011,
                "prefecture_code": waybill.HANPK02007[:2] if waybill.HANPK02007 else None
            }
            result.append(waybill_data)
            
        return result
        
    def find_previous_carrier(self, customer_id: str) -> Optional[str]:
        """
        Find the previously used carrier for a customer
        
        Args:
            customer_id: The ID of the customer
            
        Returns:
            The code of the previously used carrier, or None if not found
        """
        # Find the most recent waybill for this customer
        recent_waybill = self.db.query(Waybill).filter(
            Waybill.HANPK02002 == customer_id
        ).order_by(desc(Waybill.HANPK02REG)).first()
        
        if not recent_waybill:
            return None
            
        # Find the carrier assignment for this waybill
        carrier_assignment = self.db.query(WaybillToCarrier).filter(
            WaybillToCarrier.HANPK04001 == recent_waybill.HANPK02001
        ).first()
        
        if not carrier_assignment:
            return None
            
        return carrier_assignment.HANPK04002
        
    def select_carriers_for_picking(self, picking_id: str) -> Dict[str, Any]:
        """
        Select optimal carriers for all waybills in a picking
        
        Args:
            picking_id: The ID of the picking
            
        Returns:
            Dictionary with selection results
        """
        # Get the picking
        picking = self.db.query(PickingManagement).filter(
            PickingManagement.HANCA11001 == picking_id
        ).first()
        
        if not picking:
            return {
                "success": False,
                "message": f"Picking {picking_id} not found",
                "waybills": []
            }
            
        # Get all waybills for this picking
        waybills = self.get_picking_waybills(picking_id)
        print(f"waybills: {waybills}")
        results = []
        for waybill in waybills:
            waybill_id = waybill["waybill_id"]
            customer_id = waybill["customer_id"]
            jis_code = waybill["jis_code"]
            prefecture_code = waybill["prefecture_code"]
            parcels = waybill["parcels"]
            volume = waybill["volume"]
            weight = waybill["weight"]
            size = waybill["size"]
            shipping_date = waybill["shipping_date"]
            delivery_deadline = waybill["delivery_deadline"]
            
            # Find previously used carrier for this customer
            previous_carrier = self.find_previous_carrier(customer_id)
            
            # Calculate package metrics using fee calculator service
            parcels_count, volume, weight, size, parcels_info = self.calculate_package_metrics(waybill["products"])
            
            # Select optimal carrier using fee calculator service
            carrier_selection = self.fee_calculator.select_optimal_carrier(
                jis_code=jis_code,
                parcels=parcels_info,
                volume=volume,
                weight=weight,
                size=size,
                shipping_date=shipping_date,
                delivery_deadline=delivery_deadline,
                previous_carrier=previous_carrier
            )
            
            # Choose the best carrier (prioritize cheapest if available)
            selected_carrier = None
            selected_carrier_name = None
            
            if carrier_selection["success"]:
                # Find cheapest carrier that meets all requirements
                for carrier in carrier_selection["carriers"]:
                    if carrier["is_capacity_available"] and carrier["meets_deadline"]:
                        selected_carrier = carrier["carrier_code"]
                        selected_carrier_name = carrier["carrier_name"]
                        break
            
            if selected_carrier:
                # Update database with selected carrier
                self.update_database(waybill_id, selected_carrier)
                
                # Update SmileV database
                self.update_smilev_database(waybill_id, selected_carrier)
                
                # Update special capacity record
                if prefecture_code:
                    self.update_special_capacity(selected_carrier, prefecture_code, shipping_date)
                
            # Add result
            waybill_result = {
                "waybill_id": waybill_id,
                "success": selected_carrier is not None,
                "selected_carrier": selected_carrier,
                "carrier_name": selected_carrier_name,
                "carriers": carrier_selection.get("carriers", [])
            }
            results.append(waybill_result)
            
        return {
            "success": True,
            "message": f"Processed {len(results)} waybills",
            "waybills": results
        }
        
    def batch_select_carriers(self, picking_ids: List[str]) -> Dict[str, Any]:
        """
        Select carriers for multiple pickings
        
        Args:
            picking_ids: List of picking IDs
            
        Returns:
            Dictionary with results for all pickings
        """
        results = []
        
        for picking_id in picking_ids:
            picking_result = self.select_carriers_for_picking(picking_id)
            results.append({
                "picking_id": picking_id,
                "success": picking_result["success"],
                "message": picking_result["message"],
                "waybills_processed": len(picking_result.get("waybills", [])),
                "waybills": picking_result.get("waybills", [])
            })
            
        return {
            "success": True,
            "message": f"Processed {len(results)} pickings",
            "pickings": results
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