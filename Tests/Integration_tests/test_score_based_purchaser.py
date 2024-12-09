import unittest
from unittest.mock import patch, MagicMock
from Purchaser.score_based_purchaser import (
    fetch_sector_breakdown_from_db,
    purchase_symbol,
    rank_sectors,
    process_symbols_for_purchase
)  
from datetime import datetime
from database import metrics_DAOIMPL
import alpaca_request_methods
import logging


class TestSectorBreakdownFunctions(unittest.TestCase):

    @patch("metrics_DAOIMPL.get_last_metric_for_user")
    def test_fetch_sector_breakdown_from_db(self, mock_get_last_metric_for_user):
        """Test fetch_sector_breakdown_from_db with mocked database data."""
        mock_get_last_metric_for_user.return_value = [None, None, None, None, None, None, None, None, None, '{"Tech": 10, "Finance": 5}']
        result = fetch_sector_breakdown_from_db("profits", user_id=1)

        self.assertEqual(result, '{"Tech": 10, "Finance": 5}')
        mock_get_last_metric_for_user.assert_called_once_with(1)

    @patch("logging.info")
    def test_purchase_symbol(self, mock_logging_info):
        """Test purchase_symbol logs the correct purchase information."""
        purchase_symbol("AAPL", "Tech", 0.8, 100, 1000)
        mock_logging_info.assert_called_once_with(
            "Purchasing AAPL in sector Tech with total amount: $180.00 (Final value: 0.8)"
        )

    def test_rank_sectors(self):
        """Test rank_sectors returns correct rankings."""
        sector_breakdown = {"Tech": 10, "Finance": 5, "Healthcare": 8}
        expected_result = {"Tech": 1, "Healthcare": 2, "Finance": 3}

        result = rank_sectors(sector_breakdown)

        self.assertEqual(result, expected_result)

    @patch("alpaca_request_methods.get_symbol_current_price")
    def test_process_symbols_for_purchase(self, mock_get_symbol_current_price):
        """Test process_symbols_for_purchase generates correct orders list."""
        mock_get_symbol_current_price.side_effect = [150.0, 200.0]  # Mock prices for symbols
        symbols_list = ["AAPL", "MSFT"]
        orders = [
            {"Confidence": 0.9, "Probability": 0.8, "Sector": "Tech"},
            {"Confidence": 0.8, "Probability": 0.7, "Sector": "Finance"}
        ]
        max_total_spend = 1000

        expected_result = {
            "AAPL": {
                "symbol": "AAPL",
                "limit_price": 150.0,
                "qty": 6,  # max_total_spend / 150
                "side": "buy",
                "type": "limit",
                "tif": "day",
                "updated_last": datetime.now(),
                "confidence": 0.9,
                "probability": 0.8,
                "sector": "Tech"
            },
            "MSFT": {
                "symbol": "MSFT",
                "limit_price": 200.0,
                "qty": 5,  # max_total_spend / 200
                "side": "buy",
                "type": "limit",
                "tif": "day",
                "updated_last": datetime.now(),
                "confidence": 0.8,
                "probability": 0.7,
                "sector": "Finance"
            }
        }

        result = process_symbols_for_purchase(symbols_list, orders, max_total_spend, sectors=["Tech", "Finance"])

        # Check that keys match
        self.assertEqual(result.keys(), expected_result.keys())

        # Check each order's attributes except for `updated_last` (which is dynamic)
        for symbol in result:
            self.assertEqual(result[symbol]['symbol'], expected_result[symbol]['symbol'])
            self.assertEqual(result[symbol]['limit_price'], expected_result[symbol]['limit_price'])
            self.assertEqual(result[symbol]['qty'], expected_result[symbol]['qty'])
            self.assertEqual(result[symbol]['confidence'], expected_result[symbol]['confidence'])
            self.assertEqual(result[symbol]['probability'], expected_result[symbol]['probability'])
            self.assertEqual(result[symbol]['sector'], expected_result[symbol]['sector'])

        mock_get_symbol_current_price.assert_any_call("AAPL")
        mock_get_symbol_current_price.assert_any_call("MSFT")


if __name__ == "__main__":
    unittest.main()
