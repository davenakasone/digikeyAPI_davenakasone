"""
Unit tests for DigiKey SDK data models.
"""
import unittest

from digikey.models.barcode import BarcodeData
from digikey.models.category import Category
from digikey.models.common import PriceBreak
from digikey.models.order import LineItem, OrderStatus
from digikey.models.product import Manufacturer, ParametricAttribute, Product


class TestModels(unittest.TestCase):

    def test_price_break_from_dict(self):
        data = {"BreakQuantity": 10, "UnitPrice": 1.25}
        pb = PriceBreak.from_dict(data)
        self.assertEqual(pb.break_quantity, 10)
        self.assertEqual(pb.unit_price, 1.25)
        self.assertEqual(pb.total_price, 12.5)

    def test_product_from_dict_and_price_tier(self):
        data = {
            "DigiKeyPartNumber": "296-1411-5-ND",
            "ManufacturerProductNumber": "NE555P",
            "Description": {"ProductDescription": "IC OSC SINGLE TIMER 100KHZ 8-DIP"},
            "Manufacturer": {"Id": 296, "Name": "Texas Instruments"},
            "QuantityAvailable": 5000,
            "UnitPrice": 0.65,
            "StandardPricing": [
                {"BreakQuantity": 1, "UnitPrice": 0.65},
                {"BreakQuantity": 10, "UnitPrice": 0.55},
                {"BreakQuantity": 100, "UnitPrice": 0.40},
                {"BreakQuantity": 1000, "UnitPrice": 0.28},
            ],
            "Parameters": [
                {"ParameterId": 123, "Parameter": "Frequency", "Value": "100 kHz"},
                {"ParameterId": 456, "Parameter": "Mounting Type", "Value": "Through Hole"},
            ],
            "PrimaryDatasheet": "https://www.ti.com/lit/ds/symlink/ne555.pdf",
        }

        prod = Product.from_dict(data)
        self.assertEqual(prod.digikey_part_number, "296-1411-5-ND")
        self.assertEqual(prod.manufacturer_part_number, "NE555P")
        self.assertEqual(prod.manufacturer.name, "Texas Instruments")
        self.assertTrue(prod.in_stock)
        self.assertEqual(prod.quantity_available, 5000)
        self.assertEqual(prod.datasheet_url, "https://www.ti.com/lit/ds/symlink/ne555.pdf")

        # Parametric lookup
        self.assertEqual(prod.get_parameter("frequency"), "100 kHz")
        self.assertEqual(prod.get_parameter("Mounting Type"), "Through Hole")
        self.assertIsNone(prod.get_parameter("Nonexistent"))

        # Quantity price tier tests
        self.assertEqual(prod.unit_price_at(1), 0.65)
        self.assertEqual(prod.unit_price_at(5), 0.65)
        self.assertEqual(prod.unit_price_at(10), 0.55)
        self.assertEqual(prod.unit_price_at(50), 0.55)
        self.assertEqual(prod.unit_price_at(100), 0.40)
        self.assertEqual(prod.unit_price_at(500), 0.40)
        self.assertEqual(prod.unit_price_at(1000), 0.28)
        self.assertEqual(prod.unit_price_at(5000), 0.28)

    def test_category_hierarchy(self):
        data = {
            "CategoryId": 1,
            "Name": "Integrated Circuits (ICs)",
            "ProductCount": 150000,
            "ChildCategories": [
                {"CategoryId": 10, "Name": "Embedded - Microcontrollers", "ProductCount": 45000},
                {"CategoryId": 20, "Name": "Clock/Timing - Programmable Timers", "ProductCount": 1200},
            ],
        }
        cat = Category.from_dict(data)
        self.assertEqual(cat.category_id, 1)
        self.assertEqual(cat.name, "Integrated Circuits (ICs)")
        self.assertEqual(len(cat.children), 2)
        self.assertEqual(cat.children[0].category_id, 10)
        self.assertEqual(cat.children[0].parent_id, 1)

    def test_barcode_data(self):
        data = {
            "DigiKeyPartNumber": "296-1411-5-ND",
            "ManufacturerPartNumber": "NE555P",
            "Quantity": 25,
            "InvoiceId": "INV-12345",
            "LotCode": "LOT9876",
        }
        barcode = BarcodeData.from_dict(data, raw_barcode="[)>06...296-1411-5-ND")
        self.assertEqual(barcode.digikey_part_number, "296-1411-5-ND")
        self.assertEqual(barcode.quantity, 25)
        self.assertEqual(barcode.invoice_id, "INV-12345")
        self.assertEqual(barcode.lot_code, "LOT9876")
        self.assertEqual(barcode.raw_barcode, "[)>06...296-1411-5-ND")

    def test_order_status(self):
        data = {
            "SalesorderId": "SO-998877",
            "Status": "Shipped",
            "OrderDate": "2026-08-19",
            "TotalPrice": 145.50,
            "Currency": "USD",
            "LineItems": [
                {
                    "LineNumber": 1,
                    "DigiKeyPartNumber": "STM32F407VGT6-ND",
                    "ManufacturerPartNumber": "STM32F407VGT6",
                    "Quantity": 10,
                    "UnitPrice": 14.55,
                    "TotalPrice": 145.50,
                    "Status": "Shipped",
                    "TrackingNumber": "1Z9999999999999999",
                }
            ],
        }
        order = OrderStatus.from_dict(data)
        self.assertEqual(order.order_id, "SO-998877")
        self.assertEqual(order.total, 145.50)
        self.assertEqual(len(order.line_items), 1)
        self.assertEqual(order.line_items[0].tracking_number, "1Z9999999999999999")


if __name__ == "__main__":
    unittest.main()
