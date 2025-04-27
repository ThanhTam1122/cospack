import unittest
from unittest.mock import MagicMock, patch
from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session

from app.services.fee_calculation_service import FeeCalculationService
from app.models.transportation_fee import TransportationFee
from app.models.transportation_company_master import TransportationCompanyMaster
from app.models.product_master import ProductMaster
from app.models.product_sub_master import ProductSubMaster


class TestFeeCalculationService(unittest.TestCase):
    def setUp(self):
        # Create a mock database session
        self.db = MagicMock(spec=Session)
        
        # Create the service with the mock db
        self.service = FeeCalculationService(self.db)
        
        # Setup mock query results for different carriers
        
        # Setup Sagawa (per-parcel pricing based on size)
        sagawa_carrier = MagicMock(spec=TransportationCompanyMaster)
        sagawa_carrier.HANMA02001 = "SAGAWA"
        sagawa_carrier.HANMA02002 = "佐川急便"
        
        # Setup Yamato (fixed price)
        yamato_carrier = MagicMock(spec=TransportationCompanyMaster)
        yamato_carrier.HANMA02001 = "YAMATO"
        yamato_carrier.HANMA02002 = "ヤマト運輸"
        
        # Set up the carrier query response
        self.db.query.return_value.filter.return_value.first.side_effect = [
            sagawa_carrier,  # First call for SAGAWA
            yamato_carrier,  # Second call for YAMATO
        ]
        
        # Setup Sagawa fee records (per parcel pricing)
        sagawa_60 = MagicMock(spec=TransportationFee)
        sagawa_60.HANMA12001 = "SAGAWA"
        sagawa_60.HANMA12002 = "1001"  # Tokyo area
        sagawa_60.HANMA12003 = Decimal('30')  # Max weight
        sagawa_60.HANMA12004 = Decimal('20')  # Max volume
        sagawa_60.HANMA12005 = Decimal('60')  # Max size (60cm)
        sagawa_60.HANMA12008 = Decimal('450')  # Base fee
        sagawa_60.HANMA12009 = Decimal('3')   # Fee type (per parcel)
        
        sagawa_80 = MagicMock(spec=TransportationFee)
        sagawa_80.HANMA12001 = "SAGAWA"
        sagawa_80.HANMA12002 = "1001"  # Tokyo area
        sagawa_80.HANMA12003 = Decimal('30')  # Max weight
        sagawa_80.HANMA12004 = Decimal('20')  # Max volume
        sagawa_80.HANMA12005 = Decimal('80')  # Max size (80cm)
        sagawa_80.HANMA12008 = Decimal('490')  # Base fee
        sagawa_80.HANMA12009 = Decimal('3')   # Fee type (per parcel)
        
        sagawa_100 = MagicMock(spec=TransportationFee)
        sagawa_100.HANMA12001 = "SAGAWA"
        sagawa_100.HANMA12002 = "1001"  # Tokyo area
        sagawa_100.HANMA12003 = Decimal('30')  # Max weight
        sagawa_100.HANMA12004 = Decimal('20')  # Max volume
        sagawa_100.HANMA12005 = Decimal('100')  # Max size (100cm)
        sagawa_100.HANMA12008 = Decimal('530')  # Base fee
        sagawa_100.HANMA12009 = Decimal('3')   # Fee type (per parcel)
        
        sagawa_120 = MagicMock(spec=TransportationFee)
        sagawa_120.HANMA12001 = "SAGAWA"
        sagawa_120.HANMA12002 = "1001"  # Tokyo area
        sagawa_120.HANMA12003 = Decimal('30')  # Max weight
        sagawa_120.HANMA12004 = Decimal('20')  # Max volume
        sagawa_120.HANMA12005 = Decimal('120')  # Max size (120cm)
        sagawa_120.HANMA12008 = Decimal('650')  # Base fee
        sagawa_120.HANMA12009 = Decimal('3')   # Fee type (per parcel)
        
        # Setup Yamato fee records (fixed price)
        yamato_fee = MagicMock(spec=TransportationFee)
        yamato_fee.HANMA12001 = "YAMATO"
        yamato_fee.HANMA12002 = "1001"  # Tokyo area
        yamato_fee.HANMA12003 = Decimal('30')  # Max weight
        yamato_fee.HANMA12004 = Decimal('20')  # Max volume
        yamato_fee.HANMA12005 = Decimal('160')  # Max size (160cm)
        yamato_fee.HANMA12006 = Decimal('0')   # Unit price per volume (not used)
        yamato_fee.HANMA12007 = Decimal('0')   # Minus volume (not used)
        yamato_fee.HANMA12008 = Decimal('800')  # Base fee
        yamato_fee.HANMA12009 = Decimal('1')   # Fee type (fixed price)
        
        # Set up fee records query response
        sagawa_fees_query = MagicMock()
        sagawa_fees_query.filter.return_value.order_by.return_value.all.return_value = [
            sagawa_120, sagawa_100, sagawa_80, sagawa_60
        ]
        
        yamato_fees_query = MagicMock()
        yamato_fees_query.filter.return_value.order_by.return_value.all.return_value = [
            yamato_fee
        ]
        
        # Configure the db query to return different fee records based on carrier code
        def get_fees_query(model):
            if model == TransportationFee:
                return MagicMock(filter=lambda *args, **kwargs: (
                    sagawa_fees_query if "SAGAWA" in str(args) else yamato_fees_query
                ))
            # For other queries, return a generic mock
            return MagicMock()
            
        self.db.query.side_effect = get_fees_query
        
        # Mock product info response
        product1 = MagicMock()
        product1.HANM003001 = 1001
        product1.HANM003002 = "Test Product 1"
        product1.HANM003004 = "個"
        product1.HANM003K007 = 1  # Inner box count
        product1.HANM003K008 = 10  # Outer box count
        product1.HANM003A005 = 1  # Set parcel count
        product1.HANM003A007 = 500  # Weight in grams
        product1.HANM003A107 = 2.5  # Volume
        
        product_sub1 = MagicMock()
        product_sub1.HANMA33001 = 1001
        product_sub1.HANMA33022 = 30  # Width
        product_sub1.HANMA33023 = 20  # Depth
        product_sub1.HANMA33024 = 10  # Height
        
        product2 = MagicMock()
        product2.HANM003001 = 1002
        product2.HANM003002 = "Test Product 2"
        product2.HANM003004 = "個"
        product2.HANM003K007 = 1  # Inner box count
        product2.HANM003K008 = 5  # Outer box count
        product2.HANM003A005 = 1  # Set parcel count
        product2.HANM003A007 = 1000  # Weight in grams
        product2.HANM003A107 = 5.0  # Volume
        
        product_sub2 = MagicMock()
        product_sub2.HANMA33001 = 1002
        product_sub2.HANMA33022 = 40  # Width
        product_sub2.HANMA33023 = 30  # Depth
        product_sub2.HANMA33024 = 20  # Height
        
        # Mock the product info query
        def get_product_info(model, product_code):
            if product_code == 1001:
                return (product1, product_sub1)
            elif product_code == 1002:
                return (product2, product_sub2)
            return None
            
        # Patch the get_product_info method
        self.service.get_product_info = MagicMock(side_effect=lambda product_code: {
            1001: {
                "product_code": 1001,
                "product_name": "Test Product 1",
                "unit": "個",
                "outer_box_count": 10,
                "inner_box_count": 1,
                "set_parcel_count": 1,
                "weight_per_unit": 0.5,  # 500g -> 0.5kg
                "volume_per_unit": 2.5,
                "outer_box_dimensions": [
                    {
                        "box_num": 1,
                        "length": 30,
                        "width": 20,
                        "height": 10
                    }
                ]
            },
            1002: {
                "product_code": 1002,
                "product_name": "Test Product 2",
                "unit": "個",
                "outer_box_count": 5,
                "inner_box_count": 1,
                "set_parcel_count": 1,
                "weight_per_unit": 1.0,  # 1000g -> 1.0kg
                "volume_per_unit": 5.0,
                "outer_box_dimensions": [
                    {
                        "box_num": 1,
                        "length": 40,
                        "width": 30,
                        "height": 20
                    }
                ]
            }
        }.get(product_code))
    
    def test_prepare_parcels_for_fee_calculation(self):
        """Test preparing parcels information for fee calculation"""
        products = [
            {"product_code": 1001, "quantity": 15},  # 1 full box (10) + 5 loose items
            {"product_code": 1002, "quantity": 8}    # 1 full box (5) + 3 loose items
        ]
        
        parcels = self.service.prepare_parcels_for_fee_calculation(products)
        
        # Should have 4 different sized parcels
        self.assertEqual(len(parcels), 4)
        
        # Check that we have the expected sizes and counts
        size_counts = {parcel["size"]: parcel["count"] for parcel in parcels}
        
        # Full box of product 1 (60cm total size)
        self.assertEqual(size_counts.get(60), 1)
        
        # Partial box of product 1 (should be smaller than 60cm)
        partial_size1 = 30 + 20 + (10 * (5/10))  # length + width + adjusted_height
        self.assertEqual(size_counts.get(partial_size1), 1)
        
        # Full box of product 2 (90cm total size)
        self.assertEqual(size_counts.get(90), 1)
        
        # Partial box of product 2
        partial_size2 = 40 + 30 + (20 * (3/5))  # length + width + adjusted_height
        self.assertEqual(size_counts.get(partial_size2), 1)
    
    def test_calculate_shipping_fee_sagawa(self):
        """Test calculating shipping fee for Sagawa Express (per-parcel pricing)"""
        # Create test parcels with different sizes
        parcels = [
            {"size": 60, "count": 2},   # 2 small boxes (60cm)
            {"size": 90, "count": 1}    # 1 medium box (90cm)
        ]
        
        # Calculate fee
        fee = self.service.calculate_shipping_fee(
            carrier_code="SAGAWA",
            area_code="1001",
            parcels=parcels,
            volume=10.0,
            weight=5.0
        )
        
        # Expected fee:
        # 2 boxes at 60cm = 2 * 450 = 900
        # 1 box at 90cm = 1 * 490 = 490
        # Total: 1390
        self.assertEqual(fee, 1390)
    
    def test_calculate_shipping_fee_yamato(self):
        """Test calculating shipping fee for Yamato Transport (fixed price)"""
        # Create test parcels with different sizes
        parcels = [
            {"size": 60, "count": 2},
            {"size": 90, "count": 1}
        ]
        
        # Calculate fee
        fee = self.service.calculate_shipping_fee(
            carrier_code="YAMATO",
            area_code="1001",
            parcels=parcels,
            volume=10.0,
            weight=5.0
        )
        
        # Expected fee: flat rate of 800
        self.assertEqual(fee, 800)
    
    def test_sagawa_mixed_parcel_sizes(self):
        """Test the Sagawa example from the user's instructions"""
        # One 60cm package and one 100cm package
        parcels = [
            {"size": 60, "count": 1},
            {"size": 100, "count": 1}
        ]
        
        fee = self.service.calculate_shipping_fee(
            carrier_code="SAGAWA",
            area_code="1001",
            parcels=parcels,
            volume=8.0,
            weight=4.0
        )
        
        # Expected fee: 450 + 530 = 980
        self.assertEqual(fee, 980)
    
    def test_calculate_package_metrics(self):
        """Test calculating all package metrics including parcels info"""
        products = [
            {"product_code": 1001, "quantity": 15},  # 1 full box (10) + 5 loose items
            {"product_code": 1002, "quantity": 8}    # 1 full box (5) + 3 loose items
        ]
        
        parcels, volume, weight, max_size, parcels_info = self.service.calculate_package_metrics(products)
        
        # Verify parcel count
        self.assertEqual(parcels, 4)  # 2 full boxes + 2 partial boxes
        
        # Verify volume calculation
        # Product 1: 15 * 2.5 = 37.5
        # Product 2: 8 * 5.0 = 40.0
        # Total: 77.5 -> round up to 78
        self.assertEqual(volume, 78)
        
        # Verify weight calculation
        # Product 1: 15 * 0.5 = 7.5kg
        # Product 2: 8 * 1.0 = 8.0kg
        # Total: 15.5kg
        # Since volume-based weight (78 * 8 = 624kg) > actual weight, use actual weight
        self.assertEqual(weight, 15.5)
        
        # Verify max size
        # Product 1 box: 30 + 20 + 10 = 60cm
        # Product 2 box: 40 + 30 + 20 = 90cm
        # Max: 90cm
        self.assertEqual(max_size, 90)
        
        # Verify parcels info
        self.assertEqual(len(parcels_info), 4)  # 4 different sized parcels
        
if __name__ == '__main__':
    unittest.main() 