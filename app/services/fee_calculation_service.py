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
from app.models.transportation_area import TransportationArea
from app.models.transportation_area_jis import TransportationAreaJISMapping
from app.models.transportation_fee import TransportationFee
from app.models.transportation_capacity import TransportationCapacity

# Setup logger
logger = logging.getLogger(__name__)

# Constants
VOLUME_CUBE_SIZE = 30.3  # cm (1 volume unit = 30.3cm cube)
VOLUME_TO_WEIGHT_RATIO = 8  # 1 volume (30.3cm cube) = 8kg


class FeeCalculationService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_product_info(self, product_code: int) -> Optional[Dict[str, Any]]:
        """
        Get product information from product master and product sub master tables
        
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
        
        # Extract product information
        result = {
            "product_code": product_code,
            "product_name": product_master.HANM003002 or "",
            "unit": product_master.HANM003004 or "",
            "set_quantity": int(product_master.HANM003006 or 1),  # Using the입수 field for set quantity
            "weight_per_unit": float(product_sub.HANMA33055 or 0),  # Individual packaging weight
            "outer_box_dimensions": {
                # Using outer box 1 dimensions by default
                "length": float(product_sub.HANMA33022 or 0),  # Width (W)
                "width": float(product_sub.HANMA33023 or 0),   # Depth (D)
                "height": float(product_sub.HANMA33024 or 0)   # Height (H)
            },
            "outer_box_count": 1,  # Default to 1 if not specified otherwise
            "outer_box_weight": float(product_sub.HANMA33025 or 0)  # Gross weight of outer box 1
        }
        
        # Try to determine outer box count based on package type info
        if product_sub.HANMA33026:  # If outer box 1 packaging type is set
            # The outer box count could be stored in a specific field or calculated
            # For now, use a default value of 1
            result["outer_box_count"] = 1
        
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
        # Calculate box volume in cm³
        box_volume_cm3 = length * width * height
        
        # Convert to volume units and round up
        volume_units = math.ceil(box_volume_cm3 / (VOLUME_CUBE_SIZE ** 3))
        
        return volume_units

    def calculate_package_metrics(self, products: List[Dict[str, Any]]) -> Tuple[int, float, float, float]:
        """
        Calculate package metrics based on products
        
        Args:
            products: List of products to ship, containing product_code and quantity
            
        Returns:
            Tuple containing (parcel_count, volume, weight, size)
        """
        total_parcels = 0
        total_volume = 0
        total_weight = 0
        max_size = 0
        
        for product_info in products:
            product_code = product_info["product_code"]
            quantity = product_info["quantity"]
            
            # Get detailed product information
            product = self.get_product_info(product_code)
            if not product:
                continue
            
            # Calculate shipping quantity
            set_quantity = product.get("set_quantity", 1)
            shipping_quantity = quantity * set_quantity
            
            # Calculate number of parcels needed
            outer_box_count = product.get("outer_box_count", 1)
            parcels = math.ceil(shipping_quantity / outer_box_count) if outer_box_count > 0 else 1
            total_parcels += parcels
            
            # Get dimensions
            dimensions = product.get("outer_box_dimensions", {})
            length = dimensions.get("length", 0)
            width = dimensions.get("width", 0)
            height = dimensions.get("height", 0)
            
            # Calculate volume
            box_volume = self.calculate_volume_from_dimensions(length, width, height)
            total_volume += box_volume * parcels
            
            # Calculate weight
            weight_per_unit = product.get("weight_per_unit", 0)
            total_weight += weight_per_unit * shipping_quantity
            
            # Calculate size (sum of three sides)
            box_size = length + width + height
            if box_size > max_size:
                max_size = box_size
        
        # Round up volume to nearest integer
        total_volume = math.ceil(total_volume)
        
        # Convert volume to weight if needed (volume-based weight)
        volume_based_weight = total_volume * VOLUME_TO_WEIGHT_RATIO
        
        # Use the larger of actual weight or volume-based weight
        effective_weight = max(total_weight, volume_based_weight)
        
        return (total_parcels, total_volume, effective_weight, max_size)

    def calculate_shipping_fee(self, carrier_code: str, area_code: int, 
                             parcels: int, volume: float, weight: float, size: float) -> Optional[float]:
        """
        Calculate shipping fee based on carrier, area, and package metrics
        
        Args:
            carrier_code: Transportation company code
            area_code: Transportation area code
            parcels: Number of parcels
            volume: Volume in volume units
            weight: Weight in kg
            size: Size (sum of three sides) in cm
            
        Returns:
            Shipping fee excluding tax, or None if calculation is not possible
        """
        # Get transportation fee records for this carrier and area
        fee_records = self.db.query(TransportationFee).filter(
            TransportationFee.carrier_code == carrier_code,
            TransportationFee.area_code == area_code
        ).order_by(
            # Order by max weight and max volume to find the appropriate tier
            TransportationFee.max_weight.desc(),
            TransportationFee.max_volume.desc()
        ).all()
        
        if not fee_records:
            logger.warning(f"No transportation fee records found for carrier {carrier_code} and area {area_code}")
            return None
        
        # Find the appropriate fee record based on weight, volume, and size
        for fee in fee_records:
            # Skip if weight exceeds max (if max is specified)
            if fee.max_weight is not None and weight > fee.max_weight:
                continue
                
            # Skip if volume exceeds max (if max is specified)
            if fee.max_volume is not None and volume > fee.max_volume:
                continue
                
            # Skip if size exceeds max (if max is specified)
            if fee.max_size is not None and size > fee.max_size:
                continue
            
            # Calculate fee based on fee type
            fee_type = fee.fee_type
            
            if fee_type == "固定額":
                # Fixed amount
                return float(fee.base_fee or 0)
                
            elif fee_type == "才数単価":
                # Volume-based pricing
                # Adjust volume by subtracting minus volume (if any)
                adjusted_volume = max(0, volume - (fee.minus_volume or 0))
                # Calculate fee: base amount + (volume * unit price)
                return float((fee.base_fee or 0) + (adjusted_volume * (fee.unit_price or 0)))
                
            elif fee_type == "個口ごと":
                # Per-parcel pricing
                return float((fee.base_fee or 0) * parcels)
        
        logger.warning(f"No suitable transportation fee record found for metrics: "
                     f"carrier={carrier_code}, area={area_code}, "
                     f"parcels={parcels}, volume={volume}, weight={weight}, size={size}")
        return None

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
            TransportationCapacity.carrier_code == carrier_code
        ).first()
        
        if not capacity:
            # If no capacity record, assume unlimited capacity
            return True
        
        # Check volume capacity
        if capacity.max_volume is not None and volume > capacity.max_volume:
            return False
            
        # Check weight capacity
        if capacity.max_weight is not None and weight > capacity.max_weight:
            return False
            
        return True

    def calculate_lead_time(self, carrier_code: str, prefecture_code: str, 
                          shipping_date: date) -> Optional[int]:
        """
        Calculate lead time based on carrier, prefecture, and shipping date
        
        Args:
            carrier_code: Transportation company code
            prefecture_code: Prefecture code (JIS)
            shipping_date: Planned shipping date
            
        Returns:
            Lead time in days, or None if calculation is not possible
        """
        # First check for special lead times
        special_lead_time = self.db.query(SpecialLeadTimeMaster).filter(
            SpecialLeadTimeMaster.HANMA41001 == carrier_code,
            SpecialLeadTimeMaster.HANMA41002 == prefecture_code,
            SpecialLeadTimeMaster.HANMA41003 == int(shipping_date.strftime('%Y%m%d'))
        ).first()
        
        if special_lead_time:
            # Calculate days between shipping date and delivery date
            delivery_date_str = str(special_lead_time.HANMA41004)
            delivery_date = date(
                int(delivery_date_str[:4]),
                int(delivery_date_str[4:6]),
                int(delivery_date_str[6:8])
            )
            return (delivery_date - shipping_date).days
        
        # Otherwise, calculate standard lead time
        # This would typically come from a standard lead time table
        # For now, use a simple calculation based on distance (prefecture code)
        # In a real implementation, you would use a more sophisticated method
        
        # Simple example: assume 1-3 days lead time
        if prefecture_code.startswith('13'):  # Tokyo
            base_lead_time = 1
        elif prefecture_code.startswith('1'):  # Hokkaido
            base_lead_time = 3
        else:
            base_lead_time = 2
        
        # Check for holidays to adjust lead time
        current_date = shipping_date
        lead_time_days = 0
        
        while lead_time_days < base_lead_time:
            current_date += timedelta(days=1)
            
            # Check if it's a weekend
            if current_date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
                continue
                
            # Check if it's a holiday
            is_holiday = self.db.query(HolidayCalendarMaster).filter(
                HolidayCalendarMaster.HANMA04002 == int(current_date.strftime('%Y%m%d'))
            ).first() is not None
            
            if is_holiday:
                continue
                
            lead_time_days += 1
        
        return base_lead_time
    
    def select_optimal_carrier(self, jis_code: str, parcels: int, volume: float, 
                           weight: float, size: float, shipping_date: date) -> Dict[str, Any]:
        """
        Select the optimal carrier based on shipping metrics and other factors
        
        Args:
            jis_code: JIS address code (5 digits)
            parcels: Number of parcels
            volume: Volume in volume units
            weight: Weight in kg
            size: Size (sum of three sides) in cm
            shipping_date: Planned shipping date
            
        Returns:
            Dictionary with carrier selection details
        """
        # Get the area code from JIS code
        prefecture_code = jis_code[:2]
        area_mapping = self.db.query(TransportationAreaJISMapping).filter(
            TransportationAreaJISMapping.jis_code == jis_code
        ).first()
        
        if not area_mapping:
            logger.warning(f"Could not find transportation area for JIS code {jis_code}")
            return {
                "success": False,
                "message": f"Could not find transportation area for JIS code {jis_code}",
                "carriers": []
            }
        
        area_code = area_mapping.area_code
        
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
            
            # Track cheapest carrier with available capacity
            if fee < cheapest_cost and has_capacity:
                cheapest_cost = fee
                cheapest_carrier = estimate
        
        # Determine the optimal carrier
        # In this simple example, we just choose the cheapest carrier
        # In a real system, you might consider other factors like lead time
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