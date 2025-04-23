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
from app.models.juhachu import JuHachuHeader, MeisaiKakucho

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

    def update_database(self, picking_id: int, waybill_data: Dict[str, Any], 
                      selected_carrier: str) -> bool:
        """
        Update the database tables with the selected carrier information
        
        Args:
            picking_id: Picking ID
            waybill_data: Waybill data dictionary
            selected_carrier: Selected carrier code
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the order numbers associated with this waybill
            order_ids = waybill_data.get("order_ids", [])
            if not order_ids:
                logger.warning(f"No order IDs found for waybill in picking {picking_id}")
                return False
            
            # 1. Update picking work table (ピッキングワーク)
            picking_works = self.db.query(PickingWork).filter(
                PickingWork.HANW002001 == picking_id,
                PickingWork.HANW002003.in_(order_ids)
            ).all()
            
            for work in picking_works:
                # Update fields as specified in requirements
                work.HANW002A002 = work.HANW002A002 or ""  # Save original value if exists
                work.HANW002A003 = selected_carrier        # Set new carrier code
            
            # 2. Update order header table (受発注ヘッダー)
            for order_id in order_ids:
                header = self.db.query(JuHachuHeader).filter(
                    JuHachuHeader.HANR004005 == order_id
                ).first()
                
                if header:
                    # Update transportation company code
                    header.HANR004A008 = selected_carrier
                
                # 3. Update detail extension table (明細拡張テーブル)
                # Find all detail extensions for this order
                extensions = self.db.query(MeisaiKakucho).filter(
                    MeisaiKakucho.HANR030001 == 1,    # Data type 1 (受発注)
                    MeisaiKakucho.HANR030002 == 1,    # Slip type 1
                    MeisaiKakucho.HANR030004 == order_id  # Order number
                ).all()
                
                for ext in extensions:
                    # Update extension fields as per requirements
                    # HANR030009 (拡張項目3) - Set to carrier code
                    ext.HANR030009 = selected_carrier
                    
                    # HANR030010 (拡張項目4) - Set to selection timestamp
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                    ext.HANR030010 = timestamp
            
            # Commit all changes
            self.db.commit()
            
            logger.info(f"Successfully updated database for picking {picking_id}, carrier {selected_carrier}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating database for picking {picking_id}: {str(e)}")
            self.db.rollback()
            return False

    def update_smilev_database(self, waybill_id: int, carrier_code: str) -> bool:
        """
        Update SmileV database with selected carrier
        """
        try:
            # Update shipping slip with selected carrier
            shipping_slip = self.db.query(ShippingSlip).filter(
                ShippingSlip.HANM009001 == waybill_id
            ).first()
            
            if shipping_slip:
                # Update carrier code
                shipping_slip.HANM009003 = carrier_code
                self.db.commit()
                
                logger.info(f"Updated SmileV: Waybill {waybill_id} assigned to carrier {carrier_code}")
                return True
            else:
                logger.warning(f"Shipping slip {waybill_id} not found for SmileV update")
                return False
                
        except Exception as e:
            logger.error(f"Error updating SmileV database: {str(e)}")
            return False

    def get_picking_waybills(self, picking_id: int) -> List[Dict[str, Any]]:
        """
        Group picking data into waybills based on the specified grouping criteria
        
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
        order_ids = list(set([work.HANW002003 for work in picking_works if work.HANW002003]))
        
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
            if work.HANW002A005 == 1:  # Assuming this field tracks processed status
                continue
                
            order_id = work.HANW002003
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
            delivery_info1 = getattr(header, "HANR004A009", None) or ""
            delivery_info2 = getattr(header, "HANR004A010", None) or ""
            
            # 6-11. Delivery destination info
            dest_name1 = getattr(header, "HANR004A035", None) or ""
            dest_name2 = getattr(header, "HANR004A036", None) or ""
            dest_postal = getattr(header, "HANR004A037", None) or ""
            dest_addr1 = getattr(header, "HANR004A039", None) or ""
            dest_addr2 = getattr(header, "HANR004A040", None) or ""
            dest_addr3 = getattr(header, "HANR004A041", None) or ""
            
            # Create the group key
            group_key = f"{shipping_date}_{delivery_date}_{customer_code}_{delivery_info1}_{delivery_info2}_{dest_name1}_{dest_name2}_{dest_postal}_{dest_addr1}_{dest_addr2}_{dest_addr3}"
            
            # Get prefecture code for lead time
            prefecture_code = getattr(header, "HANR004A031", None) or ""
            
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
                    "order_ids": []
                }
            
            # Add order ID to the waybill (for database updates)
            if order_id not in waybills[group_key]["order_ids"]:
                waybills[group_key]["order_ids"].append(order_id)
            
            # Get product information from the picking work
            product_code = work.HANW002016  # Product code
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
        Find the previously used carrier for this customer
        """
        # Look up previous successful deliveries to this customer
        recent_log = self.db.query(CarrierSelectionLog)\
            .join(ShippingSlip, ShippingSlip.HANM009001 == CarrierSelectionLog.HANM010002)\
            .filter(ShippingSlip.HANM009002 == customer_code)\
            .order_by(desc(CarrierSelectionLog.HANM010INS))\
            .first()
            
        if recent_log:
            return recent_log.HANM010008  # Return the selected carrier
            
        return None

    def select_carriers_for_picking(self, picking_id: int) -> Dict[str, Any]:
        """
        Select optimal carriers for all waybills in a picking
        
        Returns:
            Selection results
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
            area_code = None
            jis_code = waybill.get("jis_code")
            
            if jis_code:
                area_code = self.fee_calculator.get_area_code_from_jis_code(jis_code)
            elif waybill.get("postal_code"):
                jis_code = self.fee_calculator.get_postal_to_jis_mapping(waybill["postal_code"])
                if jis_code:
                    waybill["jis_code"] = jis_code  # Update the waybill with the found JIS code
                    area_code = self.fee_calculator.get_area_code_from_jis_code(jis_code)
            
            if not area_code:
                logger.warning(f"Could not determine area code for waybill {waybill['waybill_id']}, customer: {customer_code}")
                continue
            
            # Calculate package metrics using fee calculator service
            parcels, volume, weight, size = self.fee_calculator.calculate_package_metrics(waybill["products"])
            
            # Select optimal carrier using fee calculator service
            carrier_selection = self.fee_calculator.select_optimal_carrier(
                jis_code=jis_code,
                parcels=parcels,
                volume=volume,
                weight=weight,
                size=size,
                shipping_date=waybill["shipping_date"],
                delivery_deadline=waybill["delivery_date"],
                previous_carrier=previous_carrier
            )
            
            if not carrier_selection["success"]:
                logger.warning(f"Carrier selection failed for waybill {waybill['waybill_id']}: {carrier_selection['message']}")
                continue
            
            # Get selected and cheapest carrier
            selected_carrier = carrier_selection["selected_carrier"]
            cheapest_carrier = min(carrier_selection["carriers"], 
                                  key=lambda x: x["cost"])["carrier_code"] if carrier_selection["carriers"] else None
            
            # Save selection to log
            log_id = self.save_carrier_selection_log(
                waybill_id=waybill["waybill_id"],
                parcel_count=parcels,
                volume=volume,
                weight=weight,
                size=size,
                selected_carrier=selected_carrier["carrier_code"],
                cheapest_carrier=cheapest_carrier if cheapest_carrier else selected_carrier["carrier_code"],
                reason=carrier_selection["selection_reason"],
                all_carriers=carrier_selection["carriers"],
                products=waybill["products"]
            )
            
            # Update database with selection results
            self.update_database(
                picking_id=picking_id,
                waybill_data=waybill,
                selected_carrier=selected_carrier["carrier_code"]
            )
            
            # Update SmileV database
            self.update_smilev_database(
                waybill_id=waybill["waybill_id"],
                carrier_code=selected_carrier["carrier_code"]
            )
            
            # Add to results
            selection_details.append({
                "waybill_id": waybill["waybill_id"],
                "parcel_count": parcels,
                "volume": volume,
                "weight": weight,
                "size": size,
                "carrier_estimates": carrier_selection["carriers"],
                "selected_carrier_code": selected_carrier["carrier_code"],
                "selected_carrier_name": selected_carrier["carrier_name"],
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