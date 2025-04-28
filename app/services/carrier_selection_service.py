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
            HANM010006=float(size),               # Size (サイズ)
            HANM010007=cheapest_carrier,          # Cheapest carrier
            HANM010008=selected_carrier,          # Selected carrier 
            HANM010009=reason,                    # Selection reason
            HANM010INS=datetime.now()             # Insert timestamp
        )
        
        self.db.add(log)
        self.db.flush()  # To get the ID
        
        # Add product details if provided
        if products and log.HANM010001:
            for product in products:
                product_code = product["product_code"]
                dimensions = product.get("outer_box_dimensions", [{}])[0] if product.get("outer_box_dimensions") else {}
                size = float(
                    dimensions.get("length", 0) + 
                    dimensions.get("width", 0) + 
                    dimensions.get("height", 0)
                )
                
                outer_box_count = float(product.get("outer_box_count", 1) or 1)
                quantity = float(product.get("quantity", 0) or 0)
                
                box_count = math.ceil(quantity / outer_box_count)
                
                detail = CarrierSelectionLogDetail(
                    HANM011001=log.HANM010001,       # Log ID
                    HANM011002=product_code,         # Product code
                    HANM011003=int(size),            # Size
                    HANM011004=box_count             # Box count
                )
                
                self.db.add(detail)
        
        # Commit to save the log
        self.db.commit()
        
        return log.HANM010001 if log.HANM010001 else 0

    def update_database(self, waybill_id: int, parcel_count: int, 
                       volume: float, weight: float, size: float,
                       selected_carrier: str) -> bool:
        """
        Update the database tables with the selected carrier information
        
        Args:
            waybill_id: Waybill ID
            parcel_count: Parcel count
            volume: Volume
            weight: Weight
            size: Size
            selected_carrier: Selected carrier code
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Find the waybill
            waybill = self.db.query(Waybill).filter(
                Waybill.HANPK02001 == waybill_id
            ).first()
            
            if not waybill:
                logger.warning(f"Waybill {waybill_id} not found in the database")
                return False
            
            # Update fields
            waybill.HANPK02008 = parcel_count
            waybill.HANPK02009 = volume
            waybill.HANPK02010 = weight
            waybill.HANPK02011 = size
            
            # Update carrier
            waybill.HANPK04002 = selected_carrier
            
            # Update timestamp
            waybill.HANPK04UPD = datetime.now().strftime("%Y%m%d%H%M%S%f")[:20]
            
            # Commit changes
            self.db.commit()
            
            logger.info(f"Successfully updated database for waybill {waybill_id}, carrier {selected_carrier}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating database for waybill {waybill_id}: {str(e)}")
            self.db.rollback()
            return False

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
            
    def get_picking_waybills(self, picking_id: int) -> List[Dict[str, Any]]:
        """
        Group picking data into waybills based on the specified grouping criteria
        
        Args:
            picking_id: Picking ID to process
            
        Returns:
            List of waybill data dictionaries
        """
        # Get all picking works and related order data for this picking ID
        picking_works = self.db.query(PickingWork).filter(
            PickingWork.HANW002009 == picking_id
        ).all()
        
        if not picking_works:
            logger.warning(f"No picking works found for picking ID {picking_id}")
            return []
        
        # Group by delivery destination, shipping date, delivery date, etc. as specified
        waybills = {}
        
        # Get order IDs from the picking works
        order_ids = list(set([work.HANW002002 for work in picking_works if work.HANW002002]))
        
        # Get order headers and grouping data
        order_headers = {}
        for order_id in order_ids:
            header = self.db.query(JuHachuHeader).filter(
                JuHachuHeader.HANR004005 == order_id
            ).first()
            
            if header:
                order_headers[order_id] = header
        
        # Group picking works into waybills based on the specified criteria
        for work in picking_works:
            # Skip if the work is already processed or not active
            if work.HANW002A005 == "1":  # Processed status flag
                continue
                
            order_id = work.HANW002002
            header = order_headers.get(order_id)

            if not header:
                logger.warning(f"Order header not found for order {order_id}")
                continue
            
            # Build grouping key based on the specified criteria
            # 1. HANR004015 - 入出荷予定日 (Planned shipping date)
            shipping_date = getattr(header, "HANR004015", None) or ""
            # 2. HANR004006 - 納期日 (Delivery date)
            delivery_date = getattr(header, "HANR004006", None) or ""
            # 3. HANR004002 - 取引先コード (Customer code)
            customer_code = getattr(header, "HANR004002", None) or ""
            # 4-5. HANR004A009, HANR004A010 - 納期情報1, 納期情報2 (Delivery info)
            delivery_info1 = header.HANR004A009 or ""
            delivery_info2 = header.HANR004A010 or ""
            
            # 6-11. Delivery destination info
            dest_name1 = header.HANR004A035 or ""
            dest_name2 = header.HANR004A036 or ""
            dest_postal = header.HANR004A037 or ""
            dest_addr1 = header.HANR004A039 or ""
            dest_addr2 = header.HANR004A040 or ""
            dest_addr3 = header.HANR004A041 or ""
            
            # Create the group key - items sharing the same key will be shipped together
            group_key = f"{shipping_date}_{delivery_date}_{customer_code}_{delivery_info1}_{delivery_info2}_{dest_name1}_{dest_name2}_{dest_postal}_{dest_addr1}_{dest_addr2}_{dest_addr3}"
            
            # Get prefecture code for lead time
            prefecture_code = header.HANR004A031 or ""

            # Get or create waybill group
            if group_key not in waybills:
                # Parse dates
                try:
                    shipping_date_obj = date(
                        int(str(shipping_date)[0:4]),
                        int(str(shipping_date)[4:6]),
                        int(str(shipping_date)[6:8])
                    ) if shipping_date and len(str(shipping_date)) >= 8 else date.today()
                    
                    delivery_date_obj = date(
                        int(str(delivery_date)[0:4]),
                        int(str(delivery_date)[4:6]),
                        int(str(delivery_date)[6:8])
                    ) if delivery_date and len(str(delivery_date)) >= 8 else shipping_date_obj
                except (ValueError, TypeError):
                    shipping_date_obj = date.today()
                    delivery_date_obj = date.today()

                # Get JIS code from postal code if available
                jis_code = None
                if dest_postal:
                    jis_code = self.fee_calculator.get_postal_to_jis_mapping(dest_postal)
                
                waybills[group_key] = {
                    "waybill_id": len(waybills) + 1,  # Temporary ID
                    "customer_code": customer_code,
                    "prefecture_code": prefecture_code,
                    "jis_code": jis_code,
                    "postal_code": dest_postal,
                    "shipping_date": shipping_date_obj,
                    "delivery_date": delivery_date_obj,
                    "products": [],
                    "order_ids": [],
                    "picking_works": []  # Store references to the picking works for later update
                }
            
            # Add order ID to the waybill (for database updates)
            if order_id not in waybills[group_key]["order_ids"]:
                waybills[group_key]["order_ids"].append(order_id)
            
            # Add the picking work reference for later update
            waybills[group_key]["picking_works"].append(work)
            
            # Get product information from the picking work
            product_code = work.HANW002030  # Product code
            quantity = work.HANW002041 or 0  # 出荷数量 (Shipping quantity)
            
            if quantity <= 0:
                continue
            
            # Get product details
            product_info = self.fee_calculator.get_product_info(product_code)

            if product_info:
                waybills[group_key]["products"].append({
                    "product_code": product_code,
                    "quantity": quantity,
                    "set_parcel_count": product_info.get("set_parcel_count", 1),
                    "outer_box_count": product_info.get("outer_box_count", 1),
                    "weight_per_unit": product_info.get("weight_per_unit", 0),
                    "volume_per_unit": product_info.get("volume_per_unit", 0),
                    "outer_box_dimensions": product_info.get("outer_box_dimensions", [])
                })
            else:
                # If product info not found, use default values
                logger.warning(f"Product info not found for code {product_code}, using defaults")
                waybills[group_key]["products"].append({
                    "product_code": product_code,
                    "quantity": quantity,
                    "set_parcel_count": 1,
                    "outer_box_count": 1,
                    "weight_per_unit": 1.0,
                    "volume_per_unit": 0,
                    "outer_box_dimensions": []
                })
        
        return list(waybills.values())

    def find_previous_carrier(self, customer_code: str) -> Optional[str]:
        """
        Find the previously used carrier for a customer
        
        Args:
            customer_code: Customer code
            
        Returns:
            The carrier code, or None if not found
        """
        # Look up the most recent order for this customer with a carrier assigned
        recent_header = self.db.query(JuHachuHeader).filter(
            JuHachuHeader.HANR004002 == customer_code,
            JuHachuHeader.HANR004A008 != None,  # Has a carrier assigned
            JuHachuHeader.HANR004A008 != ""     # Non-empty carrier code
        ).order_by(
            desc(JuHachuHeader.HANR004914)     # Most recent
        ).first()
        
        if recent_header and recent_header.HANR004A008:
            return recent_header.HANR004A008
        
        return None

    def select_carriers_for_picking(self, picking_id: int) -> Dict[str, Any]:
        """
        Select optimal carriers for all waybills in a picking
        
        Args:
            picking_id: The ID of the picking
            
        Returns:
            Dictionary with selection results
        """
        # Check if picking exists
        picking = self.db.query(PickingManagement).filter(
            PickingManagement.HANCA11001 == picking_id
        ).first()
        
        if not picking:
            return {
                "picking_id": picking_id,
                "waybill_count": 0,
                "selection_details": [],
                "success": False,
                "message": f"Picking ID {picking_id} not found"
            }
            
        # Get waybills from picking data
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
            customer_code = waybill.get("customer_code", "")
            # Find previously used carrier for this customer for consistency
            previous_carrier = self.find_previous_carrier(customer_code)
            
            # Get area code from JIS code or postal code
            jis_code = waybill.get("jis_code")
            if not jis_code and waybill.get("postal_code"):
                jis_code = self.fee_calculator.get_postal_to_jis_mapping(waybill["postal_code"])
                if jis_code:
                    waybill["jis_code"] = jis_code
            
            if not jis_code:
                logger.warning(f"Could not determine JIS code for waybill, customer: {customer_code}")
                continue
                
            prefecture_code = jis_code[:2] if jis_code and len(jis_code) >= 2 else None
            if not prefecture_code:
                logger.warning(f"Could not extract prefecture code from JIS code {jis_code}")
                continue
            
            try:
                # Calculate package metrics using fee calculator service
                parcels, volume, weight, max_size, parcels_info = self.calculate_package_metrics(waybill["products"])
                
                # Convert values to float to avoid Decimal type issues
                volume = float(volume)
                weight = float(weight)
                max_size = float(max_size)
                
                # Select optimal carrier using fee calculator service
                carrier_selection = self.fee_calculator.select_optimal_carrier(
                    jis_code=jis_code,
                    parcels=parcels_info,
                    volume=volume,
                    weight=weight,
                    size=max_size,
                    shipping_date=waybill["shipping_date"],
                    delivery_deadline=waybill["delivery_date"],
                    previous_carrier=previous_carrier
                )
                
                if not carrier_selection["success"]:
                    logger.warning(f"Carrier selection failed for waybill, customer: {customer_code}, message: {carrier_selection['message']}")
                    continue
                
                # Get selected and cheapest carrier
                selected_carrier = carrier_selection["selected_carrier"]
                cheapest_carrier = None
                for carrier in carrier_selection["carriers"]:
                    if carrier["is_capacity_available"]:
                        if cheapest_carrier is None or carrier["cost"] < cheapest_carrier["cost"]:
                            cheapest_carrier = carrier
                
                cheapest_carrier_code = cheapest_carrier["carrier_code"] if cheapest_carrier else selected_carrier["carrier_code"]
                
                # Save selection to log
                log_id = self.save_carrier_selection_log(
                    waybill_id=waybill["waybill_id"],
                    parcel_count=int(parcels),
                    volume=volume,
                    weight=weight,
                    size=max_size,
                    selected_carrier=selected_carrier["carrier_code"],
                    cheapest_carrier=cheapest_carrier_code,
                    reason=carrier_selection["selection_reason"],
                    all_carriers=carrier_selection["carriers"],
                    products=waybill["products"]
                )
                
                # Update database with selection results
                self.update_database(
                    waybill_id=waybill["waybill_id"],
                    parcel_count=int(parcels),
                    volume=volume,
                    weight=weight,
                    size=max_size,
                    selected_carrier=selected_carrier["carrier_code"]
                )
                
                # Update special capacity for the prefecture
                if prefecture_code:
                    self.update_special_capacity(
                        carrier_code=selected_carrier["carrier_code"],
                        prefecture_code=prefecture_code,
                        shipping_date=waybill["shipping_date"]
                    )
                
                # Add to results
                selection_details.append({
                    "waybill_id": waybill["waybill_id"],
                    "parcel_count": int(parcels),
                    "volume": volume,
                    "weight": weight,
                    "size": max_size,
                    "carrier_estimates": carrier_selection["carriers"],
                    "selected_carrier_code": selected_carrier["carrier_code"],
                    "selected_carrier_name": selected_carrier["carrier_name"],
                    "selection_reason": carrier_selection["selection_reason"]
                })
            except Exception as e:
                logger.error(f"Error processing waybill for customer {customer_code}: {str(e)}")
                continue
        
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
        
        Args:
            picking_ids: List of picking IDs
            
        Returns:
            Batch selection results
        """
        results = []
        success_count = 0
        failed_pickings = []
        
        for picking_id in picking_ids:
            result = self.select_carriers_for_picking(picking_id)
            results.append(result)
            
            if result["success"]:
                success_count += 1
            else:
                failed_pickings.append(picking_id)
        
        return {
            "results": results,
            "success": success_count > 0,
            "message": f"Processed {len(picking_ids)} pickings, {success_count} successful, {len(failed_pickings)} failed",
            "failed_pickings": failed_pickings
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