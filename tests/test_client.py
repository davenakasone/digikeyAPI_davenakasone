"""
Unit tests for unified DigiKey facade client.
"""
import unittest
from unittest.mock import MagicMock, patch

from digikey.client import DigiKey
from digikey.models.product import Product


class TestDigiKeyClientFacade(unittest.TestCase):

    def setUp(self):
        self.mock_creds_patch = patch(
            "digikey.client.resolve_credentials"
        )
        self.mock_resolve = self.mock_creds_patch.start()
        self.mock_resolve.return_value = MagicMock(
            client_id="test_id",
            client_secret="test_secret",
            redirect_uri="https://localhost",
            environment="production",
        )

    def tearDown(self):
        self.mock_creds_patch.stop()

    def test_client_initialization_and_services(self):
        dk = DigiKey()
        self.assertIsNotNone(dk.products)
        self.assertIsNotNone(dk.reference)
        self.assertIsNotNone(dk.barcode)
        self.assertIsNotNone(dk.orders)
        self.assertIsNotNone(dk.mylists)
        self.assertIsNotNone(dk.quotes)

    def test_client_search_shortcut(self):
        dk = DigiKey()
        dk.products.search = MagicMock(return_value="mock_page")

        res = dk.search("microcontroller", limit=20)
        self.assertEqual(res, "mock_page")
        dk.products.search.assert_called_once_with(keywords="microcontroller", limit=20)

    def test_client_get_details_shortcut(self):
        dk = DigiKey()
        dk.products.get_details = MagicMock(return_value="mock_product")

        res = dk.get_details("296-1411-5-ND")
        self.assertEqual(res, "mock_product")
        dk.products.get_details.assert_called_once_with(part_number="296-1411-5-ND")


if __name__ == "__main__":
    unittest.main()
