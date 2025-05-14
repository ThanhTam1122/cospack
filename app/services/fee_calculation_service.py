from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from typing import List, Optional, Dict, Any, Tuple, Union
from datetime import date, datetime, timedelta
import math
import logging
from decimal import Decimal

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
MAX_SET_PARCEL_COUNT = 100  # Maximum supported set parcel count


class FeeCalculationService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_postal_to_jis_mapping(self, postal_code: str) -> Optional[str]:
        """
        Get JIS code from postal code
        """
        if not postal_code:
            return None
            
        try:
            mapping = self.db.query(PostalJISMapping).filter(
                PostalJISMapping.HANMA45002 == postal_code
            ).first()
            
            if mapping:
                return mapping.HANMA45001
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching JIS code for postal code {postal_code}: {str(e)}")
            return None

    def get_area_code_from_jis(self, jis_code: str) -> Optional[int]:
        """
        Get transportation area code from JIS address code
        """
        if not jis_code:
            return None
            
        try:
            mapping = self.db.query(TransportationAreaJISMapping).filter(
                TransportationAreaJISMapping.HANMA44002 == jis_code
            ).first()
            
            if mapping:
                return mapping.HANMA44001
            
            logger.warning(f"Could not find transportation area for JIS code {jis_code}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching area code for JIS code {jis_code}: {str(e)}")
            return None

    def trim_string(self, value: Any) -> str:
        """
        Trim whitespace from string values
        
        Args:
            value: The value to trim
            
        Returns:
            Trimmed string or original value if not a string
        """
        if isinstance(value, str):
            return value.strip()
        return value

    def get_product_info(self, product_code: int) -> Optional[Dict[str, Any]]:
        """
        Get product information from product master and product sub master tables
        based on the new requirements
        
        Args:
            product_code: The product code to retrieve information for
            
        Returns:
            Dictionary containing product information or None if product not found
        """
        # Trim whitespace from product code if it's a string
        original_product_code = product_code
        if isinstance(product_code, str):
            product_code = product_code.strip()
            if product_code != original_product_code:
                logger.info(f"Trimmed product code from '{original_product_code}' to '{product_code}'")
            
        # Query both product master and product sub master
        product = self.db.query(
            ProductMaster, ProductSubMaster
        ).join(
            ProductSubMaster, 
            ProductMaster.HANM003001 == ProductSubMaster.HANMA33001
        ).filter(
            ProductMaster.HANM003001 == product_code,
            ProductSubMaster.HANMA33001 == product_code
        ).first()
        
        if not product:
            logger.warning(f"Product with code '{product_code}' not found in database")
            return None
        
        product_master, product_sub = product
        # Extract product information based on the requirements
        result = {
            "product_code": self.trim_string(product_code),
            "product_name": self.trim_string(product_master.HANM003002 or ""),
            "unit": self.trim_string(product_master.HANM003004 or ""),
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
            logger.warning(f"Product '{product_code}' has set_parcel_count={result['set_parcel_count']} "
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
            
        logger.info(f"Product info retrieved for '{product_code}': volume={result['volume_per_unit']}, weight={result['weight_per_unit']}, outer_box_count={result['outer_box_count']}")
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
        if not products:
            logger.warning("Empty products list provided to calculate_package_metrics")
            return 0, 0.0, 0.0, 0.0, []
            
        logger.info(f"Starting package metrics calculation for {len(products)} products")
        
        total_parcels = 0
        total_volume = 0.0
        total_weight = 0.0
        max_size = 0.0
        parcels_info = []
        
        for product_info in products:
            product_code = product_info["product_code"]
            # Ensure quantity is a float to avoid Decimal multiplication issues
            quantity = self.to_float(product_info["quantity"])
            
            # Ensure product code is trimmed
            if isinstance(product_code, str):
                product_code = product_code.strip()
                
            logger.info(f"Calculating metrics for product: '{product_code}', quantity: {quantity}")
            
            if quantity <= 0:
                logger.warning(f"Skipping product '{product_code}' - quantity is {quantity} (≤ 0)")
                continue
            
            # Get detailed product information
            product_details = self.get_product_info(product_code)
            if not product_details:
                logger.warning(f"Skipping product '{product_code}' - product details not found in database")
                continue
            
            # Get key product metrics and ensure they are integers
            set_parcel_count = self.to_int(product_details.get("set_parcel_count", 1))
            outer_box_count = self.to_int(product_details.get("outer_box_count", 1))
            
            if outer_box_count <= 0:
                logger.warning(f"Product '{product_code}' has invalid outer_box_count: {outer_box_count}, using 1 instead")
                outer_box_count = 1  # Prevent division by zero
                
            # Calculate complete boxes and remaining items
            # Use integer division and modulo for integer results
            quantity_int = self.to_int(quantity)
            complete_boxes = quantity_int // outer_box_count
            remaining_items = quantity_int % outer_box_count
            
            # Calculate parcels needed based on set_parcel_count
            parcels_for_complete_boxes = complete_boxes * set_parcel_count
            
            # Calculate parcels for remaining items (if any)
            parcels_for_remaining = 0
            if remaining_items > 0:
                parcels_for_remaining = set_parcel_count
            
            # Total parcels for this product
            product_parcels = parcels_for_complete_boxes + parcels_for_remaining
            total_parcels += product_parcels
            
            logger.info(f"Product '{product_code}': quantity={quantity}, outer_box_count={outer_box_count}, "
                       f"complete_boxes={complete_boxes}, remaining_items={remaining_items}, "
                       f"parcels={product_parcels}, volume_per_unit: {product_details['volume_per_unit']}")
                
            # Calculate volume
            if product_details.get("volume_per_unit", 0) > 0:
                # If volume is directly provided, use it - ensure float conversion
                volume_per_unit = self.to_float(product_details["volume_per_unit"])
                product_volume = volume_per_unit * quantity
                total_volume += product_volume
                logger.info(f"Using direct volume for '{product_code}': {volume_per_unit} × {quantity} = {product_volume}")
            else:
                # Calculate from dimensions if available
                box_dimensions = product_details.get("outer_box_dimensions", [])
                
                if box_dimensions:
                    logger.info(f"Calculating volume from {len(box_dimensions)} box dimensions for '{product_code}'")
                    # Calculate volume for each box set
                    for box_idx, box_dim in enumerate(box_dimensions):
                        # If this is beyond our parcel count, skip
                        if box_idx >= set_parcel_count:
                            break
                            
                        # Ensure dimensions are converted to float
                        length = self.to_float(box_dim.get("length", 0))
                        width = self.to_float(box_dim.get("width", 0))
                        height = self.to_float(box_dim.get("height", 0))
                        
                        if length <= 0 or width <= 0 or height <= 0:
                            logger.warning(f"Box {box_idx+1} for product '{product_code}' has invalid dimensions: "
                                          f"{length} × {width} × {height}")
                            continue
                            
                        # Complete boxes
                        if box_idx == 0:
                            # For the first box type (or if only one type)
                            box_volume = self.calculate_volume_from_dimensions(length, width, height)
                            volume_for_complete_boxes = box_volume * complete_boxes
                            
                            # For remaining items
                            volume_for_remaining = 0.0
                            if remaining_items > 0:
                                # Adjust height proportionally for remaining items
                                adjusted_height = height * (remaining_items / float(outer_box_count))
                                partial_box_volume = self.calculate_volume_from_dimensions(
                                    length, width, adjusted_height
                                )
                                volume_for_remaining = partial_box_volume
                                
                            product_volume = volume_for_complete_boxes + volume_for_remaining
                            total_volume += product_volume
                            
                            logger.info(f"Box {box_idx+1} volume: {length} × {width} × {height} = {box_volume} × "
                                       f"{complete_boxes} + partial({remaining_items}/{outer_box_count}) = {product_volume}")
                        else:
                            # For additional box types, just add their volumes directly
                            box_volume = self.calculate_volume_from_dimensions(length, width, height)
                            # Multiply by the quantity of items
                            box_volume_total = box_volume * quantity
                            total_volume += box_volume_total
                            
                            logger.info(f"Additional box {box_idx+1} volume: {length} × {width} × {height} = {box_volume} × "
                                       f"{quantity} = {box_volume_total}")
                else:
                    logger.warning(f"No volume or dimensions available for product '{product_code}'")
                    
            # Calculate weight
            weight_per_unit = self.to_float(product_details.get("weight_per_unit", 0))
            product_weight = weight_per_unit * quantity
            total_weight += product_weight
            
            logger.info(f"Weight for '{product_code}': {weight_per_unit} × {quantity} = {product_weight} kg")
            
            # Calculate size (max of 3 sides)
            max_product_size = 0.0
            box_dimensions = product_details.get("outer_box_dimensions", [])
            for box_dim in box_dimensions:
                # Ensure dimensions are converted to float
                length = self.to_float(box_dim.get("length", 0))
                width = self.to_float(box_dim.get("width", 0))
                height = self.to_float(box_dim.get("height", 0))
                box_size = length + width + height
                max_product_size = max(max_product_size, box_size)
                
            max_size = max(max_size, max_product_size)
            
            parcels_info.append({
                "size": max_product_size,
                "count": product_parcels
            })
            
            logger.info(f"Product '{product_code}' size: {max_product_size} cm")
        
        # Ensure metrics are positive values
        total_parcels = max(0, total_parcels)
        total_volume = max(0.0, float(total_volume))
        total_weight = max(0.0, float(total_weight))
        max_size = max(0.0, float(max_size))
        
        logger.info(f"Final package metrics: parcels={total_parcels}, volume={total_volume}, "
                   f"weight={total_weight}, max_size={max_size}")
                   
        return total_parcels, total_volume, total_weight, max_size, parcels_info

    def calculate_shipping_fee(self, carrier_code: str, area_code: int, 
                             parcels: List[Dict], volume: float, weight: float, size: float = 0) -> Optional[float]:
        """
        Calculate shipping fee based on carrier, area, and package metrics
        
        Args:
            carrier_code: Transportation company code
            area_code: Transportation area code
            parcels: List of parcels with size and count
            volume: Total volume in volume units
            weight: Total weight in kg
            size: Maximum size (sum of three sides) in cm
            
        Returns:
            Total shipping fee or None if not applicable
        """
        # Ensure all inputs are properly converted to handle Decimal/float issues
        volume = self.to_float(volume)
        weight = self.to_float(weight)
        size = self.to_float(size)
        
        logger.info(f"Calculating shipping fee: carrier={carrier_code}, area={area_code}, "
                   f"parcels={len(parcels)}, volume={volume}, weight={weight}, size={size}")
                   
        # Get transportation fee records for this carrier and area
        fee_records = self.db.query(TransportationFee).filter(
            TransportationFee.HANMA46002 == carrier_code,
            TransportationFee.HANMA46003 == str(area_code)
        ).all()

        if not fee_records:
            logger.warning(f"No transportation fee records found for carrier '{carrier_code}' and area {area_code}")
            return None

        # Calculate fee for each parcel size separately
        total_fee = 0.0
        
        # Process each parcel separately based on its size
        for parcel in parcels:
            parcel_size = self.to_float(parcel.get("size", size))
            parcel_count = self.to_int(parcel.get("count", 1))
            
            # Find the appropriate fee record for this parcel size
            applicable_records = []
            for record in fee_records:
                # Convert all values to float to avoid type issues
                max_weight = self.to_float(record.HANMA46004)
                max_volume = self.to_float(record.HANMA46005)
                max_size = self.to_float(record.HANMA46006)
                
                # Check if this record's constraints are satisfied for this parcel
                weight_ok = max_weight is None or max_weight == 0 or weight <= max_weight
                volume_ok = max_volume is None or max_volume == 0 or volume <= max_volume
                size_ok = max_size is None or max_size == 0 or parcel_size <= max_size
                
                if weight_ok and volume_ok and size_ok:
                    applicable_records.append(record)
            
            if not applicable_records:
                logger.warning(f"No applicable fee record found for parcel size {parcel_size}")
                return None
            
            # Use the most specific record for this parcel
            def record_specificity(record):
                specificity = 0
                if record.HANMA46004 is not None and record.HANMA46004 > 0:
                    specificity += 1
                if record.HANMA46005 is not None and record.HANMA46005 > 0:
                    specificity += 1
                if record.HANMA46006 is not None and record.HANMA46006 > 0:
                    specificity += 1
                return specificity
            
            applicable_records.sort(key=record_specificity, reverse=True)
            selected_record = applicable_records[0]
            
            # Calculate fee for this parcel based on its size
            fee_type = self.to_int(selected_record.HANMA46010)
            base_fee = self.to_float(selected_record.HANMA46009)
            volume_unit_price = self.to_float(selected_record.HANMA46007)
            min_threshold = self.to_float(selected_record.HANMA46008)
            
            parcel_fee = 0.0
            
            if fee_type == 1:
                # Type 1: Fixed amount
                parcel_fee = base_fee
            
            elif fee_type == 2:
                # Type 2: Volume-based price
                if volume_unit_price > 0:
                    parcel_volume = volume / len(parcels) * parcel_count
                    billable_volume = max(0, parcel_volume - min_threshold)
                    volume_fee = billable_volume * volume_unit_price
                    parcel_fee = base_fee + volume_fee
                else:
                    parcel_fee = base_fee
            
            elif fee_type == 3:
                # Type 3: Per parcel
                parcel_fee = base_fee * parcel_count
            
            else:
                # Unknown fee type, use base fee
                logger.warning(f"Unknown fee type {fee_type} for size {parcel_size}, using base fee {base_fee}")
                parcel_fee = base_fee * parcel_count
            
            total_fee += parcel_fee
        
        if total_fee <= 0:
            logger.warning(f"Calculated fee is zero or negative ({total_fee}), using null")
            return None
            
        logger.info(f"Final shipping fee across all parcel sizes: {total_fee}")
        return total_fee

    def check_carrier_capacity(self, carrier_code: str, volume: float, weight: float) -> bool:
        """
        Check if carrier has sufficient capacity for the shipment
        
        Args:
            carrier_code: Transportation company code
            volume: Shipment volume in volume units
            weight: Shipment weight in kg
            
        Returns:
            True if carrier has capacity, False otherwise
        """
        # Ensure inputs are floats
        volume = self.to_float(volume)
        weight = self.to_float(weight)
        
        logger.info(f"Checking carrier capacity: carrier='{carrier_code}', volume={volume}, weight={weight}")
        
        # Query capacity constraints for this carrier
        capacity = self.db.query(TransportationCapacity).filter(
            TransportationCapacity.HANMA47001 == carrier_code
        ).first()
        
        # If no capacity constraints found, assume carrier has capacity
        if not capacity:
            logger.info(f"No capacity constraints found for carrier '{carrier_code}' - assuming unlimited capacity")
            return True
            
        # Convert capacity values to float to avoid Decimal/float type issues
        max_volume = self.to_float(capacity.HANMA47002)
        max_weight = self.to_float(capacity.HANMA47003)
        volume_weight_ratio = self.to_float(capacity.HANMA47004)
            
        # Check volume constraint
        if max_volume > 0 and volume > max_volume:
            logger.warning(f"Carrier '{carrier_code}' capacity exceeded: volume {volume} > max {max_volume}")
            return False
            
        # Check weight constraint
        if max_weight > 0 and weight > max_weight:
            logger.warning(f"Carrier '{carrier_code}' capacity exceeded: weight {weight} > max {max_weight}")
            return False
        
        # Check if we need to apply volume-to-weight conversion
        if volume_weight_ratio > 0:
            # Convert volume to equivalent weight
            volume_as_weight = volume * volume_weight_ratio
            if volume_as_weight > max_weight:
                logger.warning(f"Carrier '{carrier_code}' capacity exceeded: volume as weight {volume_as_weight} > max weight {max_weight}")
                return False
            
        logger.info(f"Carrier '{carrier_code}' has sufficient capacity for volume={volume}, weight={weight}")
        return True

    def check_special_capacity(self, carrier_code: str, shipping_date: date, volume: float, weight: float) -> bool:
        """
        Check if carrier has special capacity limitations for the shipping date
        
        Args:
            carrier_code: Transportation company code
            shipping_date: Shipping date
            volume: Shipment volume in 才数 (capacity units)
            weight: Shipment weight in kg
            
        Returns:
            True if there is capacity available, False otherwise
        """
        # Ensure inputs are floats
        volume = self.to_float(volume)
        weight = self.to_float(weight)
        
        # Format date to integer YYYYMMDD 
        shipping_date_int = int(shipping_date.strftime('%Y%m%d'))
        
        logger.info(f"Checking special capacity: carrier='{carrier_code}', date={shipping_date_int}, volume={volume}, weight={weight}")
        
        # Query special capacity record
        special_capacity = self.db.query(SpecialCapacity).filter(
            SpecialCapacity.HANMA48001 == carrier_code,
            SpecialCapacity.HANMA48002 == shipping_date_int
        ).first()
        
        # If no special capacity record exists, capacity is unlimited
        if not special_capacity:
            logger.info(f"No special capacity restrictions for carrier '{carrier_code}' on {shipping_date_int}")
            return True
        
        # Convert capacity values to float to avoid Decimal/float type issues
        max_volume = self.to_float(special_capacity.HANMA48003)
        max_weight = self.to_float(special_capacity.HANMA48004)
        
        # Check volume constraint
        if max_volume > 0 and volume > max_volume:
            logger.warning(f"Carrier '{carrier_code}' special capacity exceeded: volume {volume} > max {max_volume}")
            return False
            
        # Check weight constraint
        if max_weight > 0 and weight > max_weight:
            logger.warning(f"Carrier '{carrier_code}' special capacity exceeded: weight {weight} > max {max_weight}")
            return False
            
        logger.info(f"Carrier '{carrier_code}' has sufficient special capacity for volume={volume}, weight={weight}")
        return True

    def is_holiday(self, check_date: date) -> bool:
        """
        Check if a date is a holiday
        
        Args:
            check_date: The date to check
            
        Returns:
            True if the date is a holiday, False otherwise
        """
        try:
            # Format the date as expected by the database (YYYYMMDD)
            date_int = int(check_date.strftime("%Y%m%d"))
            
            # Check if the date exists in the holiday calendar
            holiday = self.db.query(HolidayCalendarMaster).filter(
                HolidayCalendarMaster.HANMA04002 == date_int
            ).first()
            
            return holiday is not None
        except Exception as e:
            logger.error(f"Error checking if date {check_date} is a holiday: {str(e)}")
            return False
    
    def check_carrier_availability_on_date(self, carrier_code: str, check_date: date) -> Tuple[bool, str]:
        """
        Check if a carrier is available on a specific date
        
        Args:
            carrier_code: The carrier code
            check_date: The date to check
            
        Returns:
            Tuple of (is_available, reason) where is_available is a boolean and reason is a string
        """
        try:
            # Check if the date is a holiday
            is_holiday_date = self.is_holiday(check_date)
            
            if is_holiday_date:
                # If it's a holiday, the carrier is not available
                return False, "休日のため利用不可"
            
            return True, ""
        except Exception as e:
            logger.error(f"Error checking carrier availability on date {check_date}: {str(e)}")
            return False, f"確認エラー: {str(e)}"

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
        if self.is_holiday(shipping_date):
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
            if not self.is_holiday(current_date):
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
    
    def select_optimal_carrier(self, 
                              jis_code: str,
                              parcels: List[Dict], 
                              volume: float, 
                              weight: float, 
                              size: float,
                              shipping_date: date,
                              delivery_deadline: date,
                              previous_carrier: Optional[str] = None) -> Dict[str, Any]:
        """
        Select the optimal carrier based on the specified criteria
        
        Args:
            jis_code: The JIS code for the delivery area
            parcels: List of parcel information containing count, size, and other metrics
            volume: The total volume
            weight: The total weight
            size: The max size (sum of dimensions)
            shipping_date: The shipping date
            delivery_deadline: The delivery deadline
            previous_carrier: The previously used carrier code (optional)
            
        Returns:
            Selection results containing carrier, fee, and reason
        """
        try:
            # Get all available carriers
            carriers = self.get_available_carriers()
            
            if not carriers:
                return {
                    "success": False,
                    "message": "利用可能な運送会社がありません",
                    "carriers": []
                }
            
            # Get area code from JIS code
            area_code = self.get_area_code_from_jis(jis_code)
            if not area_code:
                return {
                    "success": False,
                    "message": f"JISコード {jis_code} に対応する配送エリアが見つかりません",
                    "carriers": []
                }
            
            # Calculate metrics for each carrier
            carrier_results = []
            
            # Track lowest cost carrier regardless of capacity or lead time
            lowest_cost_carrier = None
            lowest_cost = float('inf')
            
            for carrier in carriers:
                carrier_code = carrier.HANMA02001
                carrier_name = carrier.HANMA02002
                
                # Calculate shipping fee
                shipping_fee = self.calculate_shipping_fee(
                    carrier_code=carrier_code,
                    area_code=area_code,
                    parcels=parcels,
                    volume=volume,
                    weight=weight,
                    size=size
                )
                
                if shipping_fee is None:
                    # Skip carriers where fee calculation fails
                    continue
                
                # Track lowest cost carrier regardless of other constraints
                if shipping_fee < lowest_cost:
                    lowest_cost = shipping_fee
                    lowest_cost_carrier = {
                        "carrier_code": carrier_code,
                        "carrier_name": carrier_name,
                        "cost": shipping_fee
                    }
                
                # Calculate delivery date
                est_delivery_date, lead_time = self.calculate_delivery_date(
                    carrier_code=carrier_code,
                    area_code=area_code,
                    jis_code=jis_code,
                    shipping_date=shipping_date
                )
                
                if est_delivery_date is None:
                    # Skip carriers where delivery date calculation fails
                    continue
                
                has_capacity = self.check_carrier_capacity(carrier_code, volume, weight)
                
                # Check special capacity (if any) for the shipping date
                has_special_capacity = self.check_special_capacity(carrier_code, shipping_date, volume, weight)
                
                # Check if the carriers can meet the delivery deadline
                meets_deadline = est_delivery_date <= delivery_deadline
                
                # Determine if carrier is available for selection
                is_available = has_capacity and has_special_capacity and meets_deadline
                
                carrier_results.append({
                    "carrier_code": carrier_code,
                    "carrier_name": carrier_name,
                    "parcels": parcels,
                    "volume": volume,
                    "weight": weight,
                    "size": size,
                    "cost": shipping_fee,
                    "lead_time": lead_time,
                    "estimated_delivery_date": est_delivery_date.isoformat(),
                    "meets_deadline": meets_deadline,
                    "is_capacity_available": has_capacity and has_special_capacity,
                    "unavailable_reason": "" if is_available else self._get_unavailability_reason(
                        has_capacity, has_special_capacity, True, "", 
                        meets_deadline, est_delivery_date, delivery_deadline
                    )
                })
            
            # Sort carriers by cost (only those that meet all requirements)
            sorted_carriers = sorted(
                [c for c in carrier_results if c["is_capacity_available"] and c["meets_deadline"]],
                key=lambda x: x["cost"]
            )
            
            # Fix 3: Log cheapest carrier even when excluded
            if lowest_cost_carrier:
                logger.info(f"Lowest cost carrier: {lowest_cost_carrier['carrier_code']} - {lowest_cost_carrier['carrier_name']} (¥{lowest_cost_carrier['cost']})")
            
            # If no available carriers but we tracked the cheapest
            if not sorted_carriers and lowest_cost_carrier:
                # Add cheapest carrier to results with availability flag
                cheapest_in_results = False
                for c in carrier_results:
                    if c["carrier_code"] == lowest_cost_carrier["carrier_code"]:
                        cheapest_in_results = True
                        break
                
                if not cheapest_in_results:
                    # Add a complete record for the cheapest carrier
                    for carrier in carriers:
                        if carrier.HANMA02001 == lowest_cost_carrier["carrier_code"]:
                            est_delivery_date, lead_time = self.calculate_delivery_date(
                                carrier_code=carrier.HANMA02001,
                                area_code=area_code,
                                jis_code=jis_code,
                                shipping_date=shipping_date
                            ) or (None, 0)
                            
                            has_capacity = self.check_carrier_capacity(carrier.HANMA02001, volume, weight)
                            has_special_capacity = self.check_special_capacity(carrier.HANMA02001, shipping_date, volume, weight)
                            meets_deadline = False
                            if est_delivery_date:
                                meets_deadline = est_delivery_date <= delivery_deadline
                            
                            carrier_results.append({
                                "carrier_code": carrier.HANMA02001,
                                "carrier_name": carrier.HANMA02002,
                                "parcels": parcels,
                                "volume": volume,
                                "weight": weight,
                                "size": size,
                                "cost": lowest_cost_carrier["cost"],
                                "lead_time": lead_time if lead_time else 0,
                                "estimated_delivery_date": est_delivery_date.isoformat() if est_delivery_date else None,
                                "meets_deadline": meets_deadline,
                                "is_capacity_available": has_capacity and has_special_capacity,
                                "is_cheapest": True,
                                "unavailable_reason": "最安値ですが条件を満たしていません"
                            })
                
                return {
                    "success": False,
                    "message": "利用可能な運送会社がありません",
                    "cheapest_carrier": lowest_cost_carrier,
                    "carriers": carrier_results,
                    "selection_flags": {
                        "cheapest_carrier_logged": True,
                        "no_carriers_with_capacity": True,
                        "cannot_meet_delivery_date": True
                    }
                }
            
            if not sorted_carriers:
                return {
                    "success": False,
                    "message": "条件を満たす運送会社がありません",
                    "carriers": carrier_results,
                    "selection_flags": {
                        "no_carriers_with_capacity": True,
                        "cannot_meet_delivery_date": True
                    }
                }
            
            # Select the optimal carrier
            selected_carrier = None
            selection_reason = ""
            
            # Check if there's a preferred carrier specified
            if previous_carrier:
                # Look for the previous carrier in the sorted list
                for carrier in sorted_carriers:
                    if carrier["carrier_code"] == previous_carrier:
                        selected_carrier = carrier
                        selection_reason = "前回使用した運送会社"
                        break
            
            # If no preferred carrier or preferred carrier not found, use the cheapest carrier
            if not selected_carrier:
                selected_carrier = sorted_carriers[0]
                selection_reason = "最安値の運送会社"
            
            # Apply any special logic for carrier selection
            # For example, prefer carriers that can deliver faster if cost difference is small
            if len(sorted_carriers) > 1:
                cheapest_carrier = sorted_carriers[0]
                fastest_carrier = min(sorted_carriers, key=lambda x: x["lead_time"])
                
                # If the fastest carrier is different from the cheapest, and the cost difference is < 10%
                if fastest_carrier != cheapest_carrier and fastest_carrier["lead_time"] < cheapest_carrier["lead_time"]:
                    cost_diff_percent = (fastest_carrier["cost"] - cheapest_carrier["cost"]) / cheapest_carrier["cost"] * 100
                    
                    if cost_diff_percent < 10:
                        selected_carrier = fastest_carrier
                        selection_reason = f"最速の運送会社（最安値との差額: {cost_diff_percent:.1f}%）"
            
            return {
                "success": True,
                "selected_carrier": selected_carrier,
                "cheapest_carrier": lowest_cost_carrier or sorted_carriers[0],
                "carriers": carrier_results,
                "selection_reason": selection_reason,
                "selection_flags": {
                    "preferred_carrier_available": previous_carrier and selected_carrier["carrier_code"] == previous_carrier,
                    "preferred_carrier_unavailable": previous_carrier and selected_carrier["carrier_code"] != previous_carrier,
                    "no_preferred_carrier": not previous_carrier,
                    "fastest_carrier_selected": selection_reason.startswith("最速"),
                    "cheapest_carrier_selected": selection_reason == "最安値の運送会社",
                    "cheapest_carrier_logged": lowest_cost_carrier is not None
                }
            }
        except Exception as e:
            logger.error(f"Error selecting optimal carrier: {str(e)}")
            return {
                "success": False,
                "message": f"運送会社選定中にエラーが発生しました: {str(e)}",
                "carriers": []
            }

    def _get_unavailability_reason(self, has_capacity, has_special_capacity, 
                                 available_on_shipping_date, shipping_date_reason,
                                 meets_deadline, est_delivery_date, delivery_deadline) -> str:
        """
        Get a Japanese reason message for unavailability
        
        Args:
            has_capacity: Whether the carrier has general capacity
            has_special_capacity: Whether the carrier has special capacity for the shipping date
            available_on_shipping_date: Whether the carrier is available on the shipping date
            shipping_date_reason: Reason for shipping date unavailability
            meets_deadline: Whether the carrier can meet the delivery deadline
            est_delivery_date: The estimated delivery date
            delivery_deadline: The delivery deadline
            
        Returns:
            Reason message in Japanese
        """
        reasons = []
        
        if not has_capacity or not has_special_capacity:
            reasons.append("容量超過")
        
        if not available_on_shipping_date:
            if shipping_date_reason:
                reasons.append(shipping_date_reason)
            else:
                reasons.append("出荷日に利用不可")
        
        if not meets_deadline:
            days_late = (est_delivery_date - delivery_deadline).days
            if days_late > 0:
                reasons.append(f"納期日に間に合わず（{days_late}日遅延）")
            else:
                reasons.append("納期日に間に合いません")
        
        if not reasons:
            return "不明な理由により利用不可"
        
        return "、".join(reasons)

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

    def get_available_carriers(self) -> List[Any]:
        """
        Get all available transportation companies
        
        Returns:
            List of TransportationCompanyMaster objects
        """
        try:
            carriers = self.db.query(TransportationCompanyMaster).all()
            logger.info(f"Retrieved {len(carriers)} available carriers")
            return carriers
        except Exception as e:
            logger.error(f"Error fetching available carriers: {str(e)}")
            return []
            
    def calculate_delivery_date(self, carrier_code: str, area_code: int, jis_code: str, 
                             shipping_date: date) -> Tuple[Optional[date], Optional[int]]:
        """
        Calculate the estimated delivery date based on carrier, area, and shipping date
        
        Args:
            carrier_code: Transportation company code
            area_code: Transportation area code
            jis_code: JIS code
            shipping_date: Shipping date
            
        Returns:
            Tuple of (estimated_delivery_date, lead_time) or (None, None) if calculation fails
        """
        # Extract prefecture code from JIS code
        if not jis_code or len(jis_code) < 2:
            logger.warning(f"Invalid JIS code: {jis_code}")
            return None, None
            
        prefecture_code = jis_code[:2]
        
        # Calculate lead time
        lead_time = self.calculate_lead_time(
            carrier_code=carrier_code,
            prefecture_code=prefecture_code,
            shipping_date=shipping_date
        )
        
        if lead_time is None:
            logger.warning(f"Could not calculate lead time for carrier {carrier_code}, prefecture {prefecture_code}")
            return None, None
            
        # Calculate estimated delivery date
        estimated_delivery = shipping_date + timedelta(days=lead_time)
        
        return estimated_delivery, lead_time
        
    def get_carrier_tariff(self, carrier_code: str, area_code: int) -> Optional[Dict[str, Any]]:
        """
        Get tariff information for a carrier and area
        
        Args:
            carrier_code: The carrier code
            area_code: The transportation area code
            
        Returns:
            Dictionary with tariff information or None if not found
        """
        try:
            # Get transportation fee records for this carrier and area
            fee_records = self.db.query(TransportationFee).filter(
                TransportationFee.HANMA46002 == carrier_code,
                TransportationFee.HANMA46003 == str(area_code)
            ).all()
            
            if not fee_records:
                logger.warning(f"No tariff found for carrier {carrier_code} and area {area_code}")
                return None
                
            # Process records to create a structured tariff
            tariff = {
                "carrier_code": carrier_code,
                "area_code": area_code,
                "flat_fee": None,
                "size_fees": {}
            }
            
            # Process each fee record
            for record in fee_records:
                fee_type = self.to_int(record.HANMA46010)
                base_fee = self.to_float(record.HANMA46009)
                max_size = self.to_float(record.HANMA46006)
                
                # Store size-based fees
                if max_size > 0:
                    tariff["size_fees"][max_size] = base_fee
                # Store flat fee if no size specified
                elif tariff["flat_fee"] is None:
                    tariff["flat_fee"] = base_fee
                
            return tariff
            
        except Exception as e:
            logger.error(f"Error getting carrier tariff: {str(e)}")
            return None 