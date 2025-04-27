from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from typing import List, Optional, Dict, Any, Tuple
from datetime import date, datetime, timedelta
import math
import logging

from app.models.product_master import ProductMaster
from app.models.product_sub_master import ProductSubMaster
from app.models.holiday_calendar_master import HolidayCalendarMaster
from app.models.special_lead_time_master import SpecialLeadTimeMaster
from app.models.transportation_company_master import TransportationCompanyMaster
from app.models.transportation_company_sub_master import TransportationCompanySubMaster
from app.models.transportation_area import TransportationArea
from app.models.transportation_area_jis import TransportationAreaJISMapping
from app.models.transportation_fee import TransportationFee
from app.models.transportation_capacity import TransportationCapacity
from app.models.postal_jis_mapping import PostalJISMapping
from app.models.special_capacity import SpecialCapacity

# Setup logger
logger = logging.getLogger(__name__)

# Constants
VOLUME_CUBE_SIZE = 30.3  # cm (1 volume unit = 30.3cm cube)
VOLUME_TO_WEIGHT_RATIO = 8  # 1 volume (30.3cm cube) = 8kg
MAX_SET_PARCEL_COUNT = 5  # Maximum supported set parcel count


class FeeCalculationService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_postal_to_jis_mapping(self, postal_code: str) -> Optional[str]:
        """
        Get JIS address code from postal code using the mapping table
        
        Args:
            postal_code: Postal code
            
        Returns:
            JIS address code (5 digits)
        """
        if not postal_code:
            return None
            
        # Clean postal code format
        postal_code = postal_code.replace("-", "").strip()
        # Query the mapping table
        mapping = self.db.query(PostalJISMapping).filter(
            PostalJISMapping.HANMA45001 == postal_code
        ).first()

        if mapping:
            return mapping.HANMA45002
        return None
    
    def get_product_info(self, product_code: int) -> Optional[Dict[str, Any]]:
        """
        Get product information from product master and product sub master tables
        based on the new requirements
        
        Args:
            product_code: The product code to retrieve information for
            
        Returns:
            Dictionary containing product information or None if product not found
        """
        # Query both product master and product sub master
        product = self.db.query(
            ProductMaster, ProductSubMaster
        ).filter(
            ProductMaster.HANM003001 == product_code,
            ProductSubMaster.HANMA33001 == product_code
        ).first()
        
        if not product:
            logger.warning(f"Product with code {product_code} not found")
            return None
        
        product_master, product_sub = product
        
        # Extract product information based on the requirements
        result = {
            "product_code": product_code,
            "product_name": product_master.HANM003002 or "",
            "unit": product_master.HANM003004 or "",
            # 入数（外箱）- Outer box capacity
            "outer_box_count": int(product_master.HANM003K008 or 1),
            # 入数（内箱）- Inner box capacity 
            "inner_box_count": int(product_master.HANM003K007 or 1),
            # セット個口数量 - Set parcel count
            "set_parcel_count": int(product_master.HANM003A005 or 1),
            # 梱包重量(g) - Packaging weight in grams
            "weight_per_unit": float(product_master.HANM003A007 or 0) / 1000.0,  # Convert g to kg
            # 才数 - Volume in units
            "volume_per_unit": float(product_master.HANM003A107 or 0),
            # Outer box dimensions
            "outer_box_dimensions": []
        }
        
        # Add outer box dimensions (up to 5 sets depending on set_parcel_count)
        max_boxes = min(result["set_parcel_count"], MAX_SET_PARCEL_COUNT)
        
        # If set_parcel_count > MAX_SET_PARCEL_COUNT, log a warning
        if result["set_parcel_count"] > MAX_SET_PARCEL_COUNT:
            logger.warning(f"Product {product_code} has set_parcel_count={result['set_parcel_count']} "
                          f"which exceeds maximum supported value of {MAX_SET_PARCEL_COUNT}")
        
        # Get dimensions for all box sets
        for box_num in range(1, max_boxes + 1):
            # Get base attribute names for this box
            width_attr = f"HANMA330{21 + (box_num - 1) * 4}"
            depth_attr = f"HANMA330{22 + (box_num - 1) * 4}"
            height_attr = f"HANMA330{23 + (box_num - 1) * 4}"
            
            # Get values if attributes exist
            width = getattr(product_sub, width_attr, 0) if hasattr(product_sub, width_attr) else 0
            depth = getattr(product_sub, depth_attr, 0) if hasattr(product_sub, depth_attr) else 0
            height = getattr(product_sub, height_attr, 0) if hasattr(product_sub, height_attr) else 0
            
            # Add dimensions for this box
            result["outer_box_dimensions"].append({
                "box_num": box_num,
                "length": float(width or 0),    # W
                "width": float(depth or 0),     # D
                "height": float(height or 0)    # H
            })

        return result

    def calculate_volume_from_dimensions(self, length: float, width: float, height: float) -> float:
        """
        Calculate volume in volume units (where 1 unit = 30.3cm cube)
        
        Args:
            length: Length in cm
            width: Width in cm
            height: Height in cm
            
        Returns:
            Volume in volume units (1 unit = 30.3cm cube)
        """
        if length <= 0 or width <= 0 or height <= 0:
            return 0
            
        # Calculate box volume in cm³
        box_volume_cm3 = length * width * height
        
        # Convert to volume units and round up
        volume_units = math.ceil(box_volume_cm3 / (VOLUME_CUBE_SIZE ** 3))
        
        return volume_units

    def calculate_package_metrics(self, products: List[Dict[str, Any]]) -> Tuple[int, float, float, float, List[Dict[str, Any]]]:
        """
        Calculate package metrics based on products using the new requirements
        
        Args:
            products: List of products to ship, containing product_code and quantity
            
        Returns:
            Tuple containing (parcel_count, volume, weight, max_size, parcels_info)
        """
        total_parcels = 0
        total_volume = 0
        total_weight = 0
        max_size = 0
        
        for product_info in products:
            product_code = product_info["product_code"]
            quantity = product_info["quantity"]
            
            if quantity <= 0:
                continue
            
            # Get detailed product information
            product_details = self.get_product_info(product_code)
            if not product_details:
                logger.warning(f"Skipping product {product_code} - product details not found")
                continue
            
            # Get key product metrics
            set_parcel_count = product_details.get("set_parcel_count", 1)
            outer_box_count = product_details.get("outer_box_count", 1)
            
            if outer_box_count <= 0:
                outer_box_count = 1  # Prevent division by zero
                
            # Calculate complete boxes and remaining items
            complete_boxes = quantity // outer_box_count
            remaining_items = quantity % outer_box_count
            
            # Calculate parcels needed based on set_parcel_count
            parcels_for_complete_boxes = complete_boxes * set_parcel_count
            
            # Calculate parcels for remaining items (if any)
            parcels_for_remaining = 0
            if remaining_items > 0:
                parcels_for_remaining = set_parcel_count
            
            # Total parcels for this product
            product_parcels = parcels_for_complete_boxes + parcels_for_remaining
            total_parcels += product_parcels
            
            # Calculate volume
            if product_details.get("volume_per_unit", 0) > 0:
                # If volume is directly provided, use it
                product_volume = product_details["volume_per_unit"] * quantity
                total_volume += product_volume
            else:
                # Calculate from dimensions if available
                box_dimensions = product_details.get("outer_box_dimensions", [])
                
                if box_dimensions:
                    # Calculate volume for each box set
                    for box_idx, box_dim in enumerate(box_dimensions):
                        # If this is beyond our parcel count, skip
                        if box_idx >= set_parcel_count:
                            break
                            
                        length = box_dim.get("length", 0)
                        width = box_dim.get("width", 0)
                        height = box_dim.get("height", 0)
                        
                        # Complete boxes
                        if box_idx == 0:
                            # For the first box type (or if only one type)
                            box_volume = self.calculate_volume_from_dimensions(length, width, height)
                            volume_for_complete_boxes = box_volume * complete_boxes
                            
                            # For remaining items
                            volume_for_remaining = 0
                            if remaining_items > 0:
                                # Adjust height proportionally for remaining items
                                adjusted_height = height * (remaining_items / outer_box_count)
                                partial_box_volume = self.calculate_volume_from_dimensions(
                                    length, width, adjusted_height
                                )
                                volume_for_remaining = partial_box_volume
                                
                            total_volume += volume_for_complete_boxes + volume_for_remaining
                        else:
                            # For additional box types, just add their volumes directly
                            box_volume = self.calculate_volume_from_dimensions(length, width, height)
                            # Multiply by the quantity of items
                            box_volume_total = box_volume * quantity
                            total_volume += box_volume_total
            
            # Calculate weight - 梱包重量(g) × 出荷数量
            weight_per_unit = product_details.get("weight_per_unit", 0)
            product_weight = weight_per_unit * quantity
            total_weight += product_weight
            
            # Calculate size (sum of three sides)
            for box_dim in product_details.get("outer_box_dimensions", []):
                box_length = box_dim.get("length", 0)
                box_width = box_dim.get("width", 0)
                box_height = box_dim.get("height", 0)
                
                box_size = box_length + box_width + box_height
                
                if box_size > max_size:
                    max_size = box_size
            
            # For partial boxes, adjust the size calculation for the first box type
            if remaining_items > 0 and product_details.get("outer_box_dimensions"):
                first_box = product_details["outer_box_dimensions"][0]
                box_length = first_box.get("length", 0)
                box_width = first_box.get("width", 0)
                box_height = first_box.get("height", 0)
                
                adjusted_height = box_height * (remaining_items / outer_box_count)
                partial_box_size = box_length + box_width + adjusted_height
                
                if partial_box_size > max_size:
                    max_size = partial_box_size
        
        # Round up volume to nearest integer
        total_volume = math.ceil(total_volume)
        
        # Convert volume to weight if needed (volume-based weight)
        volume_based_weight = total_volume * VOLUME_TO_WEIGHT_RATIO
        
        # Use the larger of actual weight or volume-based weight
        effective_weight = max(total_weight, volume_based_weight)
        
        logger.info(f"Package metrics calculated: parcels={total_parcels}, volume={total_volume}, "
                   f"weight={effective_weight}, size={max_size}")
        
        # Prepare parcels info for shipping fee calculation
        parcels_info = self.prepare_parcels_for_fee_calculation(products)
        
        return (total_parcels, total_volume, effective_weight, max_size, parcels_info)

    def calculate_shipping_fee(self, carrier_code: str, area_code: int, 
                             parcels: List[Dict[str, Any]], volume: float, weight: float) -> Optional[float]:
        """
        Calculate shipping fee based on carrier, area, and package metrics
        
        Args:
            carrier_code: Transportation company code
            area_code: Transportation area code
            parcels: List of parcels with their dimensions, each containing size and count
            volume: Total volume in volume units
            weight: Total weight in kg
            
        Returns:
            Shipping fee excluding tax, or None if calculation is not possible
        """
        # Get transportation fee records for this carrier and area
        fee_records = self.db.query(TransportationFee).filter(
            TransportationFee.HANMA12001 == carrier_code,
            TransportationFee.HANMA12002 == area_code
        ).order_by(
            # Order by max weight and max volume to find the appropriate tier
            TransportationFee.HANMA12003.desc(),
            TransportationFee.HANMA12004.desc()
        ).all()
        
        if not fee_records:
            logger.warning(f"No transportation fee records found for carrier {carrier_code} and area {area_code}")
            return None
        
        # Get the fee calculation method for this carrier
        carrier = self.db.query(TransportationCompanyMaster).filter(
            TransportationCompanyMaster.HANMA02001 == carrier_code
        ).first()
        
        if not carrier:
            logger.warning(f"Carrier {carrier_code} not found")
            return None
        
        # Get fee type from the first record (all records for this carrier+area should have the same fee type)
        if not fee_records:
            return None
            
        fee_type = str(fee_records[0].HANMA12009)
        
        # Special case for carriers with per-parcel pricing based on size (like Sagawa)
        # Fee code 3: per parcel pricing
        if fee_type == "3":
            total_fee = 0
            
            # Process each parcel separately
            for parcel in parcels:
                parcel_size = parcel.get("size", 0)
                parcel_count = parcel.get("count", 1)
                
                # Find the appropriate fee record for this parcel size
                parcel_fee = None
                for fee in fee_records:
                    # Skip if size exceeds max (if max is specified)
                    if fee.HANMA12005 is not None and parcel_size > fee.HANMA12005:
                        continue
                    
                    # We found a matching fee record
                    parcel_fee = float(fee.HANMA12008 or 0)
                    break
                
                if parcel_fee is not None:
                    # Add this parcel's fee to the total
                    total_fee += parcel_fee * parcel_count
                else:
                    logger.warning(f"No fee found for parcel with size {parcel_size}")
                    # If we can't determine the fee for any parcel, return None
                    return None
            
            return total_fee
        
        # For other fee types (fixed amount or volume-based), use the first suitable fee record
        for fee in fee_records:
            # Skip if weight exceeds max (if max is specified)
            if fee.HANMA12003 is not None and weight > fee.HANMA12003:
                continue
                
            # Skip if volume exceeds max (if max is specified)
            if fee.HANMA12004 is not None and volume > fee.HANMA12004:
                continue
            
            # Calculate fee based on fee type
            if fee_type == "1":  # Fixed amount
                return float(fee.HANMA12008 or 0)
                
            elif fee_type == "2":  # Volume-based pricing
                # Adjust volume by subtracting minus volume (if any)
                adjusted_volume = max(0, volume - (fee.HANMA12007 or 0))
                # Calculate fee: base amount + (volume * unit price)
                return float((fee.HANMA12008 or 0) + (adjusted_volume * (fee.HANMA12006 or 0)))
        
        logger.warning(f"No suitable transportation fee record found for metrics: "
                     f"carrier={carrier_code}, area={area_code}, "
                     f"parcels={len(parcels)}, volume={volume}, weight={weight}")
        return None

    # Add a method to prepare parcels info for shipping fee calculation
    def prepare_parcels_for_fee_calculation(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prepare parcels information for shipping fee calculation, grouping by size
        
        Args:
            products: List of products to ship
            
        Returns:
            List of parcels with size and count
        """
        parcels = []
        
        for product_info in products:
            product_code = product_info["product_code"]
            quantity = product_info["quantity"]
            
            if quantity <= 0:
                continue
            
            # Get detailed product information
            product_details = self.get_product_info(product_code)
            if not product_details:
                logger.warning(f"Skipping product {product_code} - product details not found")
                continue
            
            # Get key product metrics
            set_parcel_count = product_details.get("set_parcel_count", 1)
            outer_box_count = product_details.get("outer_box_count", 1)
            
            if outer_box_count <= 0:
                outer_box_count = 1  # Prevent division by zero
                
            # Calculate complete boxes and remaining items
            complete_boxes = quantity // outer_box_count
            remaining_items = quantity % outer_box_count
            
            # Process each box type for this product
            box_dimensions = product_details.get("outer_box_dimensions", [])
            
            for box_idx, box_dim in enumerate(box_dimensions):
                if box_idx >= set_parcel_count:
                    break
                    
                length = box_dim.get("length", 0)
                width = box_dim.get("width", 0)
                height = box_dim.get("height", 0)
                
                # Calculate size (sum of three sides)
                size = length + width + height
                
                if box_idx == 0:
                    # For the first box type (or if only one type)
                    # Add complete boxes
                    if complete_boxes > 0:
                        parcels.append({
                            "size": size,
                            "count": complete_boxes
                        })
                    
                    # Add partial box if needed
                    if remaining_items > 0:
                        # Adjust height proportionally for remaining items
                        adjusted_height = height * (remaining_items / outer_box_count)
                        partial_box_size = length + width + adjusted_height
                        
                        parcels.append({
                            "size": partial_box_size,
                            "count": 1
                        })
                else:
                    # For additional box types, add based on total quantity
                    # Each box type will add to the parcel count based on the total quantity
                    parcels.append({
                        "size": size,
                        "count": quantity
                    })
        
        # Consolidate parcels with the same size
        consolidated_parcels = {}
        for parcel in parcels:
            size = parcel["size"]
            count = parcel["count"]
            
            if size in consolidated_parcels:
                consolidated_parcels[size] += count
            else:
                consolidated_parcels[size] = count
        
        # Convert back to list
        result = [{"size": size, "count": count} for size, count in consolidated_parcels.items()]
        
        return result

    def check_carrier_capacity(self, carrier_code: str, volume: float, weight: float) -> bool:
        """
        Check if the carrier has enough capacity for this shipment
        
        Args:
            carrier_code: Transportation company code
            volume: Volume in volume units
            weight: Weight in kg
            
        Returns:
            True if carrier has capacity, False otherwise
        """
        capacity = self.db.query(TransportationCapacity).filter(
            TransportationCapacity.HANM014001 == carrier_code
        ).first()
        
        if not capacity:
            # If no capacity record, assume unlimited capacity
            return True
        
        # Get current date
        today = date.today()
        today_str = today.strftime('%Y%m%d')
        
        # Check if capacity is applicable for today
        if (capacity.HANM014003 and str(capacity.HANM014003) > today_str) or \
           (capacity.HANM014004 and str(capacity.HANM014004) < today_str):
            # Capacity record is not applicable for today's date
            return True
        
        # Check volume capacity
        if capacity.HANM014005 is not None and volume > capacity.HANM014005:
            logger.info(f"Carrier {carrier_code} capacity exceeded: volume {volume} > max {capacity.HANM014005}")
            return False
            
        # Check weight capacity
        if capacity.HANM014006 is not None and weight > capacity.HANM014006:
            logger.info(f"Carrier {carrier_code} capacity exceeded: weight {weight} > max {capacity.HANM014006}")
            return False
            
        return True

    def check_special_capacity(self, carrier_code: str, prefecture_code: str, shipping_date: date) -> bool:
        """
        Check if the carrier has special capacity limitations for the specified
        prefecture and date
        
        Args:
            carrier_code: Transportation company code
            prefecture_code: Prefecture code
            shipping_date: Shipping date
            
        Returns:
            True if carrier has available capacity, False otherwise
        """
        # Convert date to YYYYMMDD format without hyphens
        shipping_date_str = shipping_date.strftime('%Y%m%d')
        
        # Check if there is a special capacity record for this carrier, prefecture, and date
        special_capacity = self.db.query(SpecialCapacity).filter(
            SpecialCapacity.HANMA15001 == carrier_code,
            SpecialCapacity.HANMA15002 == prefecture_code,
            SpecialCapacity.HANMA15003 == shipping_date_str
        ).first()
        
        if not special_capacity:
            # If no special capacity record, assume unlimited capacity
            return True
        
        # Check remaining capacity
        if special_capacity.HANMA15005 <= 0:
            logger.info(f"Carrier {carrier_code} has no remaining special capacity for prefecture {prefecture_code} on {shipping_date}")
            return False
        
        return True

    def is_holiday(self, check_date: date, carrier_code: str) -> bool:
        """
        Check if a date is a holiday for the given carrier
        
        Args:
            check_date: Date to check
            carrier_code: Transportation company code
            
        Returns:
            True if holiday, False otherwise
        """
        # Convert date to YYYYMMDD format as integer
        date_int = int(check_date.strftime('%Y%m%d'))
        
        # Check holiday calendar
        holiday = self.db.query(HolidayCalendarMaster).filter(
            HolidayCalendarMaster.HANMA04001 == carrier_code,
            HolidayCalendarMaster.HANMA04002 == date_int
        ).first()
        
        if holiday:
            # Check delivery status
            delivery_status = holiday.HANMA04003
            
            # If delivery_status is 0, it means no collection and no delivery
            if delivery_status == 0:
                return True
                
        # Also check if it's a weekend (Saturday or Sunday)
        if check_date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            return True
            
        return False

    def calculate_lead_time(self, carrier_code: str, prefecture_code: str, 
                          shipping_date: date) -> Optional[int]:
        """
        Calculate lead time based on carrier, prefecture, and shipping date
        using the new lead time calculation requirements
        
        Args:
            carrier_code: Transportation company code
            prefecture_code: Prefecture code (JIS)
            shipping_date: Planned shipping date
            
        Returns:
            Lead time in days, or None if calculation is not possible
        """
        # 1. Check if shipping date is a holiday
        if self.is_holiday(shipping_date, carrier_code):
            logger.info(f"Carrier {carrier_code} does not ship on {shipping_date} (holiday)")
            return None
        
        # 2. Check for special lead time
        shipping_date_int = int(shipping_date.strftime('%Y%m%d'))
        special_lead_time = self.db.query(SpecialLeadTimeMaster).filter(
            SpecialLeadTimeMaster.HANMA41001 == carrier_code,
            SpecialLeadTimeMaster.HANMA41002 == prefecture_code,
            SpecialLeadTimeMaster.HANMA41003 == shipping_date_int
        ).first()
        
        if special_lead_time:
            # Get delivery date from special lead time record
            delivery_date_str = str(special_lead_time.HANMA41004)
            if len(delivery_date_str) >= 8:
                delivery_date = date(
                    int(delivery_date_str[:4]),
                    int(delivery_date_str[4:6]),
                    int(delivery_date_str[6:8])
                )
                # Calculate lead time in days
                return (delivery_date - shipping_date).days
        
        # 3. Calculate standard lead time
        # Get the carrier's standard lead time from the sub master
        carrier_sub = self.db.query(TransportationCompanySubMaster).filter(
            TransportationCompanySubMaster.HANMA03001 == carrier_code
        ).first()
        
        if not carrier_sub:
            logger.warning(f"Carrier sub master record not found for carrier {carrier_code}")
            return None
        
        # Get standard lead time
        standard_lead_time = carrier_sub.HANMA03004
        if not standard_lead_time:
            logger.warning(f"No lead time specified for carrier {carrier_code}")
            return None
        
        # Calculate estimated delivery date
        current_date = shipping_date
        business_days = 0
        
        while business_days < standard_lead_time:
            current_date += timedelta(days=1)
            
            # Skip holidays
            if not self.is_holiday(current_date, carrier_code):
                business_days += 1
        
        # Return total number of days including holidays
        return (current_date - shipping_date).days
    
    def check_delivery_deadline(self, shipping_date: date, lead_time: int, 
                              deadline_date: date) -> bool:
        """
        Check if estimated delivery date meets the deadline
        
        Args:
            shipping_date: Shipping date
            lead_time: Lead time in days
            deadline_date: Deadline date
            
        Returns:
            True if meets deadline, False otherwise
        """
        estimated_delivery = shipping_date + timedelta(days=lead_time)
        return estimated_delivery <= deadline_date
    
    def select_optimal_carrier(self, jis_code: str, parcels: List[Dict[str, Any]], 
                               volume: float, weight: float, size: float, 
                               shipping_date: date, delivery_deadline: date = None,
                               previous_carrier: str = None) -> Dict[str, Any]:
        """
        Select the optimal carrier based on cost, lead time, and capacity
        
        Args:
            jis_code: JIS address code
            parcels: List of parcels with size and count
            volume: Volume in volume units
            weight: Weight in kg
            size: Size (sum of three sides) in cm
            shipping_date: Planned shipping date
            delivery_deadline: Optional delivery deadline
            previous_carrier: Previously used carrier for this customer
            
        Returns:
            Dictionary containing selection results
        """
        # Get area code from JIS code
        area_code = self.get_area_code_from_jis_code(jis_code)
        if not area_code:
            return {
                "success": False,
                "message": f"Unable to find area code for JIS code {jis_code}",
                "carriers": []
            }
        
        # Get prefecture code from JIS code (first 2 digits)
        prefecture_code = jis_code[:2] if jis_code and len(jis_code) >= 2 else None
        if not prefecture_code:
            return {
                "success": False,
                "message": f"Unable to extract prefecture code from JIS code {jis_code}",
                "carriers": []
            }
            
        # Get all available transportation companies
        carriers = self.db.query(TransportationCompanyMaster).filter(
            TransportationCompanyMaster.HANMA02DEL.is_(None)  # Not deleted
        ).all()
        
        if not carriers:
            return {
                "success": False,
                "message": "No transportation companies available",
                "carriers": []
            }
            
        # Prepare results
        estimates = []
        cheapest_cost = float('inf')
        cheapest_carrier = None
        fastest_lead_time = float('inf')
        fastest_carrier = None
        
        for carrier in carriers:
            carrier_code = carrier.HANMA02001
            carrier_name = carrier.HANMA02002
            
            # Skip if shipping date is a holiday for this carrier
            if self.is_holiday(shipping_date, carrier_code):
                logger.info(f"Carrier {carrier_name} skipped - does not ship on {shipping_date}")
                continue
            
            # Check if carrier has general capacity
            has_capacity = self.check_carrier_capacity(carrier_code, volume, weight)
            
            # Check if carrier has special capacity for this prefecture and date
            has_special_capacity = self.check_special_capacity(carrier_code, prefecture_code, shipping_date)
            
            # Skip if either capacity check fails
            if not has_capacity or not has_special_capacity:
                logger.info(f"Carrier {carrier_name} skipped - no capacity available")
                continue
            
            # Calculate shipping fee with parcels information
            fee = self.calculate_shipping_fee(carrier_code, area_code, parcels, volume, weight)
            
            # Calculate lead time
            lead_time = self.calculate_lead_time(carrier_code, prefecture_code, shipping_date) if prefecture_code else None
            
            # Skip carriers with no fee information or lead time
            if fee is None or lead_time is None:
                continue
            
            # Check if delivery meets deadline
            meets_deadline = True
            if delivery_deadline:
                meets_deadline = self.check_delivery_deadline(shipping_date, lead_time, delivery_deadline)
                
                # Skip carriers that can't meet the deadline
                if not meets_deadline:
                    logger.info(f"Carrier {carrier_name} skipped - cannot meet delivery deadline")
                    continue
                
            # Create carrier estimate
            estimate = {
                "carrier_code": carrier_code,
                "carrier_name": carrier_name,
                "parcel_count": len(parcels),
                "volume": volume,
                "weight": weight,
                "size": size,
                "cost": fee,
                "lead_time": lead_time,
                "is_capacity_available": has_capacity and has_special_capacity,
                "meets_deadline": meets_deadline
            }
            
            estimates.append(estimate)
            
            # Track cheapest carrier with available capacity
            if has_capacity and has_special_capacity and fee < cheapest_cost:
                cheapest_cost = fee
                cheapest_carrier = estimate
            
            # Track fastest carrier with available capacity
            if has_capacity and has_special_capacity and lead_time < fastest_lead_time:
                fastest_lead_time = lead_time
                fastest_carrier = estimate
        
        # Determine the optimal carrier
        selected_carrier = None
        selection_reason = ""
        
        # First priority: Continue using the same carrier if possible
        if previous_carrier:
            for estimate in estimates:
                if estimate["carrier_code"] == previous_carrier and estimate["is_capacity_available"]:
                    selected_carrier = estimate
                    selection_reason = "Using previously selected carrier for consistency"
                    break
        
        # Second priority: Use the cheapest carrier
        if not selected_carrier and cheapest_carrier:
            selected_carrier = cheapest_carrier
            selection_reason = "Selected lowest cost carrier"
        
        # Third priority: Use the fastest carrier if cost difference is acceptable
        if not selected_carrier and fastest_carrier:
            selected_carrier = fastest_carrier
            selection_reason = "Selected fastest carrier"
        
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