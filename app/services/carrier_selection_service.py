from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from typing import List, Optional, Dict, Any, Tuple
from datetime import date, datetime, timedelta
import math
import requests
import logging
from decimal import Decimal

from app.core.config import settings

from app.models.picking import PickingManagement, PickingDetail, PickingWork
from app.models.transportation_area_jis import TransportationAreaJISMapping
from app.models.carrier_selection_log import CarrierSelectionLog
from app.models.carrier_selection_log_detail import CarrierSelectionLogDetail
from app.models.transportation_company_master import TransportationCompanyMaster
from app.models.juhachu import JuHachuHeader, MeisaiKakucho
from app.models.waybill import Waybill

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

    def check_special_capacity(self, carrier_code: str, shipping_date: date, volume: float, weight: float) -> bool:
        """
        Check if the carrier has special capacity limitations for the shipping date
        """
        # Use the fee calculator service to check special capacity
        return self.fee_calculator.check_special_capacity(
            carrier_code=carrier_code,
            shipping_date=shipping_date,
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

    def save_carrier_selection_log(self, waybill_id: str, parcel_count: int, 
                                 volume: float, weight: float, size: float,
                                 selected_carrier: str, cheapest_carrier: str, 
                                 reason: str, products: List[Dict[str, Any]] = None) -> str:
        """
        Save the carrier selection to the log table
        
        Returns:
            The log ID (selection log code)
        """
        try:
            # Generate a unique ID for the selection log code (HANM010001)
            # Format: YYMMDDNNNN where NNNN is a sequence number (here we use milliseconds)
            now = datetime.now()
            timestamp = now.strftime("%y%m%d")  # First 6 chars: year, month, day
            milliseconds = str(int(now.timestamp() * 1000) % 10000).zfill(4)  # Last 4 chars: milliseconds padded to 4 digits
            log_id = f"{timestamp}{milliseconds}"
            
            # Create log entry
            log = CarrierSelectionLog(
                HANM010001=log_id,                        # Generated log ID
                HANM010002=waybill_id,                    # Waybill ID
                HANM010003=self.to_float(parcel_count),   # Parcel count
                HANM010004=self.to_float(volume),         # Volume (才数)
                HANM010005=self.to_float(weight),         # Weight (重量)
                HANM010006=selected_carrier,              # Selected carrier 
                HANM010007=cheapest_carrier,              # Cheapest carrier
                HANM010008=reason,                        # Selection reason
                HAN10M010_INS= datetime.now().strftime("%Y%m%d%H%M%S%f")[:20]
            )
            
            self.db.add(log)
            self.db.flush()  # To get the ID
            
            # Add product details if provided
            if products and log.HANM010001:
                # Check if product details already exist
                existing_details = self.db.query(CarrierSelectionLogDetail).filter(
                    CarrierSelectionLogDetail.HANM011001 == log.HANM010001
                ).all()
                
                if existing_details:
                    # Delete existing details to replace with new ones
                    for detail in existing_details:
                        self.db.delete(detail)
                
                for product in products:
                    product_code = product["product_code"]
                    dimensions = product.get("outer_box_dimensions", [{}])[0] if product.get("outer_box_dimensions") else {}
                    size = self.to_float(
                        dimensions.get("length", 0) + 
                        dimensions.get("width", 0) + 
                        dimensions.get("height", 0)
                    )
                    
                    outer_box_count = self.to_float(product.get("outer_box_count", 1) or 1)
                    quantity = self.to_float(product.get("quantity", 0) or 0)
                    
                    box_count = math.ceil(quantity / outer_box_count)
                    
                    detail = CarrierSelectionLogDetail(
                        HANM011001=log.HANM010001,       # Log ID
                        HANM011002=product_code,         # Product code
                        HANM011003=self.to_float(size),  # Size
                        HANM011004=self.to_float(box_count)  # Box count
                    )
                    
                    self.db.add(detail)
            
            # Commit to save the log
            self.db.commit()
            logger.info(f"Saved carrier selection log with ID: {log_id}")
            return log_id
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving carrier selection log: {str(e)}")
            return ""

    def update_database(self, shipping_date: date, delivery_deadline: date,
                        customer_code: str, postal_code: str = "",
                        delivery_info1: str = "", delivery_info2: str = "",
                        delivery_name1: str = "", delivery_name2: str = "",
                        delivery_address1: str = "", delivery_address2: str = "",
                        delivery_address3: str = "") -> str:
        """
        Create a new waybill record using the Waybill model
        
        Args:
            shipping_date: Planned shipping date
            delivery_deadline: Delivery deadline date
            customer_code: Customer code
            postal_code: Postal code
            delivery_info1: Delivery destination info 1
            delivery_info2: Delivery destination info 2
            delivery_name1: Delivery destination name 1
            delivery_name2: Delivery destination name 2
            delivery_address1: Delivery address 1
            delivery_address2: Delivery address 2
            delivery_address3: Delivery address 3
            
        Returns:
            The created waybill ID as a string, or empty string on failure
        """
        try:
            # Generate waybill ID with timestamp (WB + YYYYMMDDhhmmss)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            waybill_id = f"WB{timestamp}"
            
            # Create new waybill record
            waybill = Waybill(
                HANM009001=waybill_id,                    # Waybill code
                HANM009002=shipping_date,                 # Planned shipping date
                HANM009003=delivery_deadline,             # Delivery date
                HANM009004=int(customer_code) if customer_code.isdigit() else 0,    # Customer code
                HANM009005=delivery_info1[:128] if delivery_info1 else None,        # Delivery info 1
                HANM009006=delivery_info2[:128] if delivery_info2 else None,        # Delivery info 2
                HANM009007=delivery_name1[:64] if delivery_name1 else None,         # Delivery name 1
                HANM009008=delivery_name2[:64] if delivery_name2 else None,         # Delivery name 2
                HANM009009=postal_code[:16] if postal_code else None,               # Postal code
                HANM009010=delivery_address1[:128] if delivery_address1 else None,  # Address 1
                HANM009011=delivery_address2[:128] if delivery_address2 else None,  # Address 2
                HANM009012=delivery_address3[:128] if delivery_address3 else None   # Address 3
            )
            
            # Add to session and flush to get the ID
            self.db.add(waybill)
            self.db.flush()
            
            # Commit changes
            self.db.commit()
            
            logger.info(f"Successfully created waybill with ID {waybill_id}")
            return waybill_id
            
        except Exception as e:
            logger.error(f"Error creating waybill record: {str(e)}")
            self.db.rollback()
            return ""

    def update_smilev_database(self, waybill_id: str, carrier_code: str, order_ids: List[str] = None, picking_works: List[PickingWork] = None) -> bool:
        """
        Update the SmileV database tables with the selected carrier information
        
        Args:
            waybill_id: The ID of the waybill
            carrier_code: The code of the selected transportation company
            order_ids: List of order IDs related to this waybill
            picking_works: List of picking work records related to this waybill
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current timestamp for updates - use numeric format only (YYYYMMDDHHMMSS)
            timestamp = self.to_float(datetime.now().strftime("%Y%m%d%H%M%S"))
            update_count = 0
            
            # 1. Update JuHachuHeader table (受発注ヘッダーテーブル)
            if order_ids:
                for order_id in order_ids:
                    # Find the order header
                    header = self.db.query(JuHachuHeader).filter(
                        JuHachuHeader.HANR004005 == order_id
                    ).first()
                    
                    if header:
                        # Check if carrier is already assigned
                        current_carrier = header.HANR004A008
                        if current_carrier and current_carrier.strip() == carrier_code.strip():
                            logger.info(f"Carrier {carrier_code} is already assigned to order {order_id}")
                            continue
                        
                        # Store original carrier code if not already set
                        original_carrier = header.HANR004A008
                        
                        # Update carrier code field (HANR004A008)
                        header.HANR004A008 = carrier_code
                        
                        # Update timestamp
                        header.HANR004UPD = timestamp
                        
                        # Find related MeisaiKakucho records (明細拡張テーブル)
                        meisai_records = self.db.query(MeisaiKakucho).filter(
                            MeisaiKakucho.HANR030001 == 2,               # データ種別=2 (fixed for order data)
                            MeisaiKakucho.HANR030002 == header.HANR004004, # 伝票区分
                            MeisaiKakucho.HANR030003 == 0,               # 明細区分=0 (fixed as normal)
                            MeisaiKakucho.HANR030004 == order_id,        # 連番 (order number)
                            MeisaiKakucho.HANR030005 == 0                # 行No=0 (fixed)
                        ).all()
                        
                        # Update MeisaiKakucho if found
                        for meisai in meisai_records:
                            # Store original carrier code in extension field 3
                            meisai.HANR030009 = original_carrier or ""
                            
                            # Store new carrier code in extension field 4
                            meisai.HANR030010 = carrier_code
                            
                            # Update timestamp
                            meisai.HANR030UPD = timestamp
                            
                        update_count += 1
                        logger.info(f"Updated order header {order_id} with carrier code {carrier_code}")
            
            # 2. Update PickingWork table (ピッキングワーク)
            if picking_works:
                for work in picking_works:
                    # Check if carrier is already assigned
                    current_carrier = work.HANW002A003
                    if current_carrier and current_carrier.strip() == carrier_code.strip():
                        logger.info(f"Carrier {carrier_code} is already assigned to picking work {work.HANW002001}-{work.HANW002002}-{work.HANW002003}")
                        continue
                    
                    # Store original carrier code if not already set
                    if not work.HANW002A002 or work.HANW002A002 == "":
                        work.HANW002A002 = work.HANW002A003 or ""
                    
                    # Update changed carrier code
                    work.HANW002A003 = carrier_code
                    
                    # Update timestamp
                    work.HANW002UPD = timestamp
                    
                    update_count += 1
                    logger.info(f"Updated picking work {work.HANW002001}-{work.HANW002002}-{work.HANW002003} with carrier code {carrier_code}")
            
            # Commit all changes
            if update_count > 0:
                self.db.commit()
                logger.info(f"Successfully updated {update_count} records in SmileV database for waybill {waybill_id}")
                return True
            else:
                logger.info(f"No records needed updating for waybill {waybill_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating SmileV database for waybill {waybill_id}: {str(e)}")
            self.db.rollback()
            return False

    def get_picking_waybills(self, picking_id: int) -> List[Dict[str, Any]]:
        """
        Group picking data into waybills based on the specified grouping criteria
        
        Args:
            picking_id: Picking ID to process
            
        Returns:
            List of waybill data dictionaries
        """
        logger.info(f"Getting waybills for picking ID {picking_id}")
        
        # Get all picking works and related order data for this picking ID
        picking_works = self.db.query(PickingWork).filter(
            PickingWork.HANW002009 == picking_id
        ).all()
        
        if not picking_works:
            logger.warning(f"No picking works found for picking ID {picking_id}")
            return []
            
        logger.info(f"Found {len(picking_works)} picking work records for picking ID {picking_id}")
        
        # Group by delivery destination, shipping date, delivery date, etc. as specified
        waybills = {}
        
        # Get order IDs from the picking works
        order_ids = list(set([work.HANW002002 for work in picking_works if work.HANW002002]))
        
        logger.info(f"Processing {len(order_ids)} unique order IDs from picking works")
        
        # Get order headers and grouping data
        order_headers = {}
        for order_id in order_ids:
            # Only include orders where carrier code is None or empty
            # Also filter by document type as requested
            query = self.db.query(JuHachuHeader).filter(
                JuHachuHeader.HANR004005 == order_id,
                JuHachuHeader.HANR004004.in_(['1', '2', '3'])
            )

            if not settings.ENV == "Development":
                query = query.filter(JuHachuHeader.HANR004A008 == settings.CARRIER_UNASSIGNED_CODE)

            header = query.first()
            
            if header:
                order_headers[order_id] = header
            else:
                logger.info(f"Order header not found or already has carrier code assigned for order ID {order_id}")
                
        logger.info(f"Found {len(order_headers)} order headers with no carrier assigned out of {len(order_ids)} order IDs")
        
        # If no valid order headers found, return empty list
        if not order_headers:
            logger.info(f"No orders without assigned carriers found for picking ID {picking_id}")
            return []
        
        # Group picking works into waybills based on the specified criteria
        for work in picking_works:
            order_id = work.HANW002002
            header = order_headers.get(order_id)

            if not header:
                logger.info(f"Order header not found or already has carrier assigned for order {order_id}, skipping work item {work.HANW002001}-{work.HANW002002}-{work.HANW002003}")
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
            dest_postal = (header.HANR004A037 or "").replace("-", "").strip()
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
                    
                    logger.info(f"Parsed shipping date: {shipping_date} -> {shipping_date_obj}, delivery date: {delivery_date} -> {delivery_date_obj}")
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error parsing dates from shipping_date={shipping_date}, delivery_date={delivery_date}: {str(e)}")
                    shipping_date_obj = date.today()
                    delivery_date_obj = date.today()

                # Get JIS code from postal code if available
                jis_code = None
                if dest_postal:
                    jis_code = self.fee_calculator.get_postal_to_jis_mapping(dest_postal)
                    if jis_code:
                        logger.info(f"Found JIS code {jis_code} for postal code {dest_postal}")
                    else:
                        logger.warning(f"Could not find JIS code for postal code {dest_postal}")
                
                logger.info(f"Creating new waybill group with key: {group_key}")
                waybills[group_key] = {
                    "customer_code": customer_code,
                    "prefecture_code": prefecture_code,
                    "delivery_info1": delivery_info1,
                    "delivery_info2": delivery_info2,
                    "dest_name1": dest_name1,
                    "dest_name2": dest_name2,
                    "dest_postal": dest_postal,
                    "dest_addr1": dest_addr1,
                    "dest_addr2": dest_addr2,
                    "dest_addr3": dest_addr3,
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
                logger.warning(f"Skipping product {product_code} with quantity {quantity} (≤ 0)")
                continue
            
            # Trim product code
            original_product_code = product_code
            if isinstance(product_code, str):
                product_code = product_code.strip()
                if product_code != original_product_code:
                    logger.info(f"Trimmed product code from '{original_product_code}' to '{product_code}'")
            
            # Get product details
            product_info = self.fee_calculator.get_product_info(product_code)

            if product_info:
                # Convert quantity to float for safe calculations
                quantity_float = self.to_float(quantity)
                
                # Use float conversions throughout to avoid Decimal-float multiplication issues
                waybills[group_key]["products"].append({
                    "product_code": product_code,
                    "quantity": quantity_float,
                    "set_parcel_count": self.to_int(product_info.get("set_parcel_count", 1)),
                    "outer_box_count": self.to_int(product_info.get("outer_box_count", 1)),
                    "weight_per_unit": self.to_float(product_info.get("weight_per_unit", 0)),
                    "volume_per_unit": self.to_float(product_info.get("volume_per_unit", 0)),
                    "outer_box_dimensions": self._convert_dimensions_to_float(product_info.get("outer_box_dimensions", []))
                })
            else:
                # If product info not found, use default values
                # Convert quantity to float for safe calculations
                quantity_float = self.to_float(quantity)
                
                logger.warning(f"Product info not found for code '{product_code}', using default values")
                waybills[group_key]["products"].append({
                    "product_code": product_code,
                    "quantity": quantity_float,
                    "set_parcel_count": 1,
                    "outer_box_count": 1,
                    "weight_per_unit": 1.0,
                    "volume_per_unit": 0.0,
                    "outer_box_dimensions": []
                })
                
        logger.info(f"Created {len(waybills)} waybill groups from {len(picking_works)} picking works")
        return list(waybills.values())

    def find_previous_carrier_for_waybill(self, waybill: Dict[str, Any]) -> Optional[str]:
        """
        Find the previously used carrier for a waybill with the same destinations
        
        Args:
            waybill: Waybill information including customer_code, postal_code, etc.
            
        Returns:
            The carrier code, or None if not found
        """
        try:
            customer_code = waybill.get("customer_code", "")
            shipping_date = waybill.get("shipping_date", "")
            delivery_date = waybill.get("delivery_date", "")
            shipping_date_str = shipping_date.strftime("%Y%m%d") if shipping_date else ""
            delivery_date_str = delivery_date.strftime("%Y%m%d") if delivery_date else ""
            delivery_info1 = waybill.get("delivery_info1", "")
            delivery_info2 = waybill.get("delivery_info2", "")
            dest_name1 = waybill.get("dest_name1", "")
            dest_name2 = waybill.get("dest_name2", "")
            dest_postal = waybill.get("dest_postal", "")
            dest_addr1 = waybill.get("dest_addr1", "")
            dest_addr2 = waybill.get("dest_addr2", "")
            dest_addr3 = waybill.get("dest_addr3", "")

            print(f"customer_code       : {customer_code}")
            print(f"shipping_date_str   : {shipping_date_str}")
            print(f"delivery_date_str   : {delivery_date_str}")
            print(f"delivery_info1      : {delivery_info1}")
            print(f"delivery_info2      : {delivery_info2}")
            print(f"dest_name1          : {dest_name1}")
            print(f"dest_name2          : {dest_name2}")
            print(f"dest_postal         : {dest_postal}")
            print(f"dest_addr1          : {dest_addr1}")
            print(f"dest_addr2          : {dest_addr2}")
            print(f"dest_addr3          : {dest_addr3}")
            
            recent_headers = self.db.query(Waybill).filter(
                Waybill.HANM009004 == customer_code,    # Same customer
                Waybill.HANM009002 == shipping_date_str,    # Same shipping date
                Waybill.HANM009003 == delivery_date_str,    # Same delivery date
                Waybill.HANM009005 == delivery_info1,  # Same delivery infomation1
                Waybill.HANM009006 == delivery_info2,  # Same delivery_infomation2
                Waybill.HANM009007 == dest_name1,      # Same destination name1
                Waybill.HANM009008 == dest_name2,      # Same destination name2
                Waybill.HANM009009 == dest_postal,     # Same destination postal code
                Waybill.HANM009010 == dest_addr1,      # Same delivery address1
                Waybill.HANM009011 == dest_addr2,      # Same delivery address2
                Waybill.HANM009012 == dest_addr3,      # Same delivery address3
            ).order_by(
                desc(Waybill.HANM009002)                # Most recent by update date
            ).limit(10).all()

            if recent_headers and len(recent_headers) > 0:
                # Return the most recently used carrier for the same destination
                waybill_code = recent_headers[0].HANM009001

                carrier_selection_log = self.db.query(CarrierSelectionLog).filter(
                    CarrierSelectionLog.HANM010002 == waybill_code
                ).order_by(
                    desc(CarrierSelectionLog.HAN10M010_INS)
                ).limit(10).all()
                
                if carrier_selection_log and len(carrier_selection_log) > 0:
                    return carrier_selection_log[0].HANM010007
        except Exception as e:
            logger.error(f"Error in find_previous_carrier_for_waybill: {str(e)}")
            return None

    def select_carriers_for_picking(self, picking_id: int) -> Dict[str, Any]:
        """
        Select optimal carriers for all waybills in a picking
        
        Args:
            picking_id: The ID of the picking
            
        Returns:
            Dictionary with selection results
        """
        logger.info(f"Starting carrier selection for picking ID {picking_id}")
        
        # Check if picking exists
        picking = self.db.query(PickingManagement).filter(
            PickingManagement.HANCA11001 == picking_id
        ).first()
        
        if not picking:
            logger.warning(f"Picking ID {picking_id} not found in database")
            return {
                "picking_id": picking_id,
                "waybill_count": 0,
                "selection_details": [],
                "success": False,
                "message": f"Picking ID {picking_id} not found"
            }
            
        # Check if the picking has any associated orders before trying to get waybills
        picking_work_count = self.db.query(PickingWork).filter(
            PickingWork.HANW002009 == picking_id
        ).count()
        
        if picking_work_count == 0:
            logger.warning(f"No picking works found for picking ID {picking_id}")
            return {
                "picking_id": picking_id,
                "waybill_count": 0,
                "selection_details": [],
                "success": False,
                "message": f"No orders found for picking ID {picking_id}"
            }
        
        # Get all orders associated with this picking
        all_order_ids = self.db.query(PickingWork.HANW002002).filter(
            PickingWork.HANW002009 == picking_id
        ).distinct().all()
        all_order_ids = [order_id[0] for order_id in all_order_ids if order_id[0]]
        
        # Check if any orders have carriers already assigned
        orders_with_carriers = self.db.query(JuHachuHeader).filter(
            JuHachuHeader.HANR004005.in_(all_order_ids),
            JuHachuHeader.HANR004A008 != None,
            JuHachuHeader.HANR004A008 != ''
        ).count()
        
        # Get waybills from picking data
        waybills = self.get_picking_waybills(picking_id)
        
        if not waybills:
            # If we found orders with carriers assigned, and that's the same as the total order count,
            # then all orders already have carriers assigned
            if orders_with_carriers > 0 and orders_with_carriers == len(all_order_ids):
                logger.info(f"All orders in picking ID {picking_id} already have carriers assigned")
                return {
                    "picking_id": picking_id,
                    "waybill_count": 0,
                    "selection_details": [],
                    "success": True,
                    "message": f"All orders in picking ID {picking_id} already have carriers assigned"
                }
            elif orders_with_carriers > 0:
                # Some orders have carriers assigned, but not all
                logger.warning(f"No eligible waybills found for picking ID {picking_id}, {orders_with_carriers} of {len(all_order_ids)} orders already have carriers assigned")
                return {
                    "picking_id": picking_id,
                    "waybill_count": 0,
                    "selection_details": [],
                    "success": True,
                    "message": f"No eligible waybills found for picking ID {picking_id}, {orders_with_carriers} of {len(all_order_ids)} orders already have carriers assigned"
                }
            else:
                # No orders have carriers assigned, but there might be other issues
                logger.warning(f"No waybills could be created from orders in picking ID {picking_id}")
                return {
                    "picking_id": picking_id,
                    "waybill_count": 0,
                    "selection_details": [],
                    "success": False,
                    "message": f"No waybills could be created from orders in picking ID {picking_id}. Check for missing product info or delivery details."
                }
            
        logger.info(f"Processing {len(waybills)} waybills for picking ID {picking_id}")
        
        selection_details = []
        successful_selections = 0
        failed_selections = 0
        
        for waybill_index, waybill in enumerate(waybills, 1):
            # Skip waybills with no products
            if not waybill.get("products") or len(waybill.get("products", [])) == 0:
                logger.warning(f"Skipping waybill {waybill_index}/{len(waybills)} - no products found")
                failed_selections += 1
                continue
            
            customer_code = waybill.get("customer_code", "")
            logger.info(f"Processing waybill {waybill_index}/{len(waybills)}, customer: '{customer_code}'")
            
            # Find previously used carrier for this waybill's destination for consistency
            previous_carrier = self.find_previous_carrier_for_waybill(waybill)
            if previous_carrier:
                logger.info(f"Found previously used carrier '{previous_carrier}' for waybill destination")
            else:
                logger.info(f"No previous carrier found for waybill destination, checking customer history")
                
            # Get area code from JIS code or postal code
            jis_code = waybill.get("jis_code")

            if not jis_code and waybill.get("postal_code"):
                logger.info(f"Attempting to find JIS code from postal code '{waybill['postal_code']}'")
                jis_code = self.fee_calculator.get_postal_to_jis_mapping(waybill["postal_code"])
                if jis_code:
                    logger.info(f"Found JIS code '{jis_code}' for postal code '{waybill['postal_code']}'")
                    waybill["jis_code"] = jis_code
                else:
                    logger.warning(f"Failed to find JIS code for postal code '{waybill['postal_code']}'")
            
            if not jis_code:
                logger.warning(f"Could not determine JIS code for waybill {waybill_index}, customer: '{customer_code}'")
                failed_selections += 1
                continue
                
            prefecture_code = jis_code[:2] if jis_code and len(jis_code) >= 2 else None
            if not prefecture_code:
                logger.warning(f"Could not extract prefecture code from JIS code '{jis_code}'")
                failed_selections += 1
                continue
                
            logger.info(f"Using prefecture code '{prefecture_code}' from JIS code '{jis_code}'")
            
            try:
                # Calculate package metrics using fee calculator service
                logger.info(f"Calculating package metrics for waybill {waybill_index} with {len(waybill['products'])} products")
                parcels, volume, weight, max_size, parcels_info = self.calculate_package_metrics(waybill["products"])
                
                # Skip if no valid parcels were calculated
                if parcels == 0 or volume == 0 or weight == 0:
                    logger.warning(f"Skipping waybill {waybill_index} - invalid package metrics: parcels={parcels}, volume={volume}, weight={weight}")
                    failed_selections += 1
                    continue
                
                # Convert values to float to avoid Decimal type issues
                volume = self.to_float(volume)
                weight = self.to_float(weight)
                max_size = self.to_float(max_size)
                
                logger.info(f"Package metrics for waybill {waybill_index}: parcels={parcels}, volume={volume}, weight={weight}, size={max_size}")
                
                # Select optimal carrier using fee calculator service
                logger.info(f"Selecting optimal carrier for waybill {waybill_index}")
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
                    logger.warning(f"Carrier selection failed for waybill {waybill_index}, customer: '{customer_code}', reason: {carrier_selection['message']}")
                    failed_selections += 1
                    continue
                    
                logger.info(f"Carrier selection successful for waybill {waybill_index}")
                
                # Find the absolute cheapest carrier regardless of capacity/lead time
                absolute_cheapest_carrier = None
                for carrier in carrier_selection["carriers"]:
                    if absolute_cheapest_carrier is None or carrier["cost"] < absolute_cheapest_carrier["cost"]:
                        absolute_cheapest_carrier = carrier
                
                # Selected carrier (one that meets all constraints)
                selected_carrier = carrier_selection["selected_carrier"]
                final_carrier_code = selected_carrier["carrier_code"]
                
                # Get cheapest carrier that meets capacity constraints
                viable_cheapest_carrier = None
                for carrier in carrier_selection["carriers"]:
                    if carrier["is_capacity_available"]:
                        if viable_cheapest_carrier is None or carrier["cost"] < viable_cheapest_carrier["cost"]:
                            viable_cheapest_carrier = carrier
                
                # Determine if we should use the unassigned carrier code when no viable carriers exist
                use_unassigned_code = False
                
                if not [c for c in carrier_selection["carriers"] if c.get("is_capacity_available", False)]:
                    logger.info(f"No carriers with sufficient capacity/lead time, using unassigned code")
                    final_carrier_code = settings.CARRIER_UNASSIGNED_CODE
                    use_unassigned_code = True
                    reason_message = f"全ての運送会社がリードタイムまたはキャパシティを超過、最安: {viable_cheapest_carrier['carrier_code']}"
                
                # Log the decision
                logger.info(f"Final carrier selection: '{final_carrier_code}', reason: {reason_message}")
                
                # Set carrier code for database updates (must define before using below)
                carrier_code_to_use = final_carrier_code
                
                # Create waybill record
                logger.info(f"Creating waybill record for waybill group {waybill_index}")
                waybill_id = self.update_database(
                    shipping_date=waybill["shipping_date"],
                    delivery_deadline=waybill["delivery_date"],
                    customer_code=customer_code,
                    postal_code=waybill["postal_code"],
                    delivery_info1=waybill.get("delivery_info1", ""),
                    delivery_info2=waybill.get("delivery_info2", ""),
                    delivery_name1=waybill.get("delivery_name1", ""),
                    delivery_name2=waybill.get("delivery_name2", ""),
                    delivery_address1=waybill.get("delivery_address1", ""),
                    delivery_address2=waybill.get("delivery_address2", ""),
                    delivery_address3=waybill.get("delivery_address3", "")
                )
                
                # Check if waybill creation failed
                if not waybill_id:
                    logger.warning(f"Failed to create waybill record for waybill {waybill_index}")
                    failed_selections += 1
                    continue
                
                # Save selection to log - always save the absolute cheapest carrier for reference
                logger.info(f"Saving carrier selection log for waybill {waybill_index}")
                log_id = self.save_carrier_selection_log(
                    waybill_id=waybill_id,
                    parcel_count=int(parcels),
                    volume=volume,
                    weight=weight,
                    size=max_size,
                    selected_carrier=carrier_code_to_use,
                    cheapest_carrier=viable_cheapest_carrier["carrier_code"] if viable_cheapest_carrier else "",
                    reason=reason_message,  # Use the detailed reason message
                    products=waybill["products"]
                )
                
                if not log_id:
                    logger.warning(f"Failed to save carrier selection log for waybill {waybill_index}")
                    failed_selections += 1
                    continue
                
                # Update SmileV database tables with carrier selection - use the carrier_code_to_use
                logger.info(f"Updating SmileV database tables for waybill {waybill_index}")
                smilev_update_success = self.update_smilev_database(
                    waybill_id=waybill_id,
                    carrier_code=carrier_code_to_use,  # Use either selected or unassigned code
                    order_ids=waybill["order_ids"],
                    picking_works=waybill["picking_works"]
                )
                
                if not smilev_update_success:
                    logger.warning(f"Failed to update SmileV database for waybill {waybill_index}")
                    failed_selections += 1
                    continue
                
                # Add to results with both selected and cheapest carrier information
                selection_details.append({
                    "waybill_id": waybill_id,
                    "parcel_count": int(parcels),
                    "volume": volume,
                    "weight": weight,
                    "size": max_size,
                    "carrier_estimates": self._format_carrier_estimates(carrier_selection["carriers"]),
                    "selected_carrier_code": carrier_code_to_use,
                    "cheapest_carrier_code": viable_cheapest_carrier["carrier_code"] if viable_cheapest_carrier else "",
                    "selection_reason": reason_message,
                    # Get the carrier name corresponding to the final_carrier_code
                    "selected_carrier_name": "未割当" if carrier_code_to_use == settings.CARRIER_UNASSIGNED_CODE else 
                        next((c["carrier_name"] for c in carrier_selection["carriers"] if c["carrier_code"] == carrier_code_to_use), "不明")
                })
                
                successful_selections += 1
                logger.info(f"Waybill {waybill_index} processed successfully")
                
            except Exception as e:
                logger.error(f"Error processing waybill {waybill_index} for customer '{customer_code}': {str(e)}")
                failed_selections += 1
                continue
        
        logger.info(f"Carrier selection completed for picking ID {picking_id}: {successful_selections} successful, {failed_selections} failed")
        
        return {
            "picking_id": picking_id,
            "waybill_count": len(waybills),
            "selection_details": selection_details,
            "success": successful_selections > 0,
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

    def to_float(self, value: Any) -> float:
        """
        Safely convert any numeric value (including Decimal) to float
        
        Args:
            value: The value to convert
            
        Returns:
            Float value, or 0.0 if conversion fails
        """
        if value is None:
            return 0.0
            
        try:
            return float(value)
        except (ValueError, TypeError):
            logger.warning(f"Failed to convert value '{value}' to float, using 0.0 instead")
            return 0.0

    def to_int(self, value: Any) -> int:
        """
        Safely convert any numeric value to integer
        
        Args:
            value: The value to convert
            
        Returns:
            Integer value, or 0 if conversion fails
        """
        if value is None:
            return 0
            
        try:
            if isinstance(value, Decimal):
                return int(float(value))
            return int(value)
        except (ValueError, TypeError):
            logger.warning(f"Failed to convert value '{value}' to integer, using 0 instead")
            return 0

    def _convert_dimensions_to_float(self, dimensions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert dimensions from Decimal to float
        
        Args:
            dimensions: List of dimension dictionaries
            
        Returns:
            Converted list of dimension dictionaries
        """
        converted_dimensions = []
        for dim in dimensions:
            converted_dim = {k: self.to_float(v) for k, v in dim.items()}
            converted_dimensions.append(converted_dim)
        return converted_dimensions

    def _format_carrier_estimates(self, carriers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format carrier estimates to comply with the expected schema
        
        Args:
            carriers: List of carrier dictionaries
            
        Returns:
            Formatted list of carrier dictionaries
        """
        formatted_carriers = []
        for carrier in carriers:
            # Calculate parcel_count if parcels is a list of dictionaries
            parcel_count = 0
            if "parcels" in carrier and isinstance(carrier["parcels"], list):
                for parcel in carrier["parcels"]:
                    if isinstance(parcel, dict) and "count" in parcel:
                        parcel_count += self.to_int(parcel["count"])
            elif "parcel_count" in carrier:
                parcel_count = self.to_int(carrier["parcel_count"])
            
            # For is_capacity_available, consider both general capacity and special capacity if available
            is_capacity_available = carrier.get("is_capacity_available", False)
            if "is_special_capacity_available" in carrier:
                is_capacity_available = is_capacity_available and carrier["is_special_capacity_available"]
            
            formatted_carriers.append({
                "carrier_code": carrier["carrier_code"],
                "carrier_name": carrier["carrier_name"],
                "parcel_count": parcel_count,
                "volume": self.to_float(carrier["volume"]),
                "weight": self.to_float(carrier["weight"]),
                "size": self.to_float(carrier["size"]),
                "cost": self.to_float(carrier["cost"]),
                "lead_time": self.to_int(carrier["lead_time"]),
                "is_capacity_available": is_capacity_available
            })
        return formatted_carriers


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