"""
Unit tests for DigiKey API Services (Products, Reference, Barcode, Orders, Lists, Quotes).
"""
import unittest
from unittest.mock import MagicMock

from digikey.services.barcode import BarcodeService
from digikey.services.mylists import MyListsService
from digikey.services.orders import OrderService
from digikey.services.products import ProductService
from digikey.services.quotes import QuoteService
from digikey.services.reference import ReferenceService


class TestServices(unittest.TestCase):

    def setUp(self):
        self.mock_client = MagicMock()

    def test_product_service_search(self):
        self.mock_client.post.return_value = {
            "ProductsCount": 2,
            "Products": [
                {
                    "DigiKeyPartNumber": "DK-1",
                    "ManufacturerProductNumber": "MPN-1",
                    "Description": {"ProductDescription": "Part 1"},
                    "UnitPrice": 1.0,
                },
                {
                    "DigiKeyPartNumber": "DK-2",
                    "ManufacturerProductNumber": "MPN-2",
                    "Description": {"ProductDescription": "Part 2"},
                    "UnitPrice": 2.0,
                },
            ],
        }

        service = ProductService(self.mock_client)
        page = service.search(keywords="resistor", limit=5)

        self.assertEqual(page.total_count, 2)
        self.assertEqual(len(page.items), 2)
        self.assertEqual(page.items[0].digikey_part_number, "DK-1")
        self.assertEqual(page.items[1].manufacturer_part_number, "MPN-2")

        self.mock_client.post.assert_called_once()
        args, kwargs = self.mock_client.post.call_args
        self.assertEqual(args[0], "/products/v4/search/keyword")
        self.assertEqual(kwargs["json_data"]["Keywords"], "resistor")

    def test_product_service_search_with_filters(self):
        self.mock_client.post.return_value = {"ProductsCount": 0, "Products": []}
        service = ProductService(self.mock_client)
        service.search(
            keywords="capacitor",
            in_stock_only=True,
            category_id=3,
            manufacturer_id=296,
            sort_by="UnitPrice",
        )

        self.mock_client.post.assert_called_once()
        args, kwargs = self.mock_client.post.call_args
        payload = kwargs["json_data"]
        self.assertEqual(payload["Keywords"], "capacitor")
        self.assertTrue(payload["Filters"]["InStock"])
        self.assertEqual(payload["Filters"]["TaxonomyIds"], [3])
        self.assertEqual(payload["Filters"]["ManufacturerIds"], [296])
        self.assertEqual(payload["Sort"]["SortBy"], "UnitPrice")

    def test_product_service_find_alternates(self):
        self.mock_client.get.return_value = {
            "Product": {
                "DigiKeyPartNumber": "TARGET-ND",
                "ManufacturerProductNumber": "TARGET-MPN",
                "QuantityAvailable": 0,
            }
        }
        self.mock_client.post.return_value = {
            "ProductsCount": 2,
            "Products": [
                {
                    "DigiKeyPartNumber": "TARGET-ND",
                    "ManufacturerProductNumber": "TARGET-MPN",
                    "QuantityAvailable": 0,
                },
                {
                    "DigiKeyPartNumber": "ALT-1-ND",
                    "ManufacturerProductNumber": "ALT-1-MPN",
                    "QuantityAvailable": 5000,
                },
            ],
        }

        service = ProductService(self.mock_client)
        alternates = service.find_alternates("TARGET-MPN")

        self.assertEqual(len(alternates), 1)
        self.assertEqual(alternates[0].manufacturer_part_number, "ALT-1-MPN")

    def test_product_service_get_details(self):
        self.mock_client.get.return_value = {
            "Product": {
                "DigiKeyPartNumber": "DK-123",
                "ManufacturerProductNumber": "MPN-123",
                "QuantityAvailable": 100,
                "UnitPrice": 5.50,
            }
        }

        service = ProductService(self.mock_client)
        prod = service.get_details("DK-123")

        self.assertEqual(prod.digikey_part_number, "DK-123")
        self.assertEqual(prod.quantity_available, 100)
        self.assertEqual(prod.unit_price, 5.50)
        self.mock_client.get.assert_called_once_with("/products/v4/search/DK-123/productdetails")

    def test_reference_service_categories(self):
        self.mock_client.get.return_value = {
            "Categories": [
                {"CategoryId": 1, "Name": "Capacitors", "ProductCount": 50000},
                {"CategoryId": 2, "Name": "Resistors", "ProductCount": 80000},
            ]
        }

        service = ReferenceService(self.mock_client)
        categories = service.get_categories()

        self.assertEqual(len(categories), 2)
        self.assertEqual(categories[0].name, "Capacitors")
        self.assertEqual(categories[1].name, "Resistors")
        self.mock_client.get.assert_called_once_with("/products/v4/search/categories")

    def test_barcode_service_decode(self):
        self.mock_client.post.return_value = {
            "DigiKeyPartNumber": "296-1411-5-ND",
            "ManufacturerPartNumber": "NE555P",
            "Quantity": 100,
        }

        service = BarcodeService(self.mock_client)
        result = service.decode("[)>06...")

        self.assertEqual(result.digikey_part_number, "296-1411-5-ND")
        self.assertEqual(result.quantity, 100)
        self.mock_client.post.assert_called_once_with(
            "/barcode/v4/barcodedetails", json_data={"Barcode": "[)>06..."}
        )

    def test_order_service_get_status(self):
        self.mock_client.get.return_value = {
            "SalesorderId": "123456",
            "Status": "Processing",
            "TotalPrice": 250.0,
        }

        service = OrderService(self.mock_client)
        order = service.get_order_status("123456")

        self.assertEqual(order.order_id, "123456")
        self.assertEqual(order.status, "Processing")
        self.assertEqual(order.total, 250.0)

    def test_quote_service_create_quote(self):
        self.mock_client.post.return_value = {"QuoteId": "Q-999", "Status": "Submitted"}

        service = QuoteService(self.mock_client)
        res = service.create_quote([{"DigiKeyPartNumber": "DK-1", "Quantity": 500}])

        self.assertEqual(res["QuoteId"], "Q-999")
        self.mock_client.post.assert_called_once_with(
            "/quote/v1/quotes",
            json_data={"QuoteLineItems": [{"DigiKeyPartNumber": "DK-1", "Quantity": 500}]},
        )

    def test_health_inspector_all_pass(self):
        from digikey.services.doctor import HealthInspector
        self.mock_client.oauth_handler.get_valid_token.return_value = "valid_token_xyz"
        self.mock_client.post.return_value = {"ProductsCount": 1000}
        self.mock_client.get.return_value = {"Product": {"ManufacturerProductNumber": "NE555P"}}
        self.mock_client.rate_limit_remaining = 900
        self.mock_client.rate_limit_limit = 1000

        inspector = HealthInspector(self.mock_client)
        results = inspector.run_all_checks()

        self.assertEqual(len(results), 6)
        self.assertTrue(all(r.passed for r in results))


if __name__ == "__main__":
    unittest.main()
