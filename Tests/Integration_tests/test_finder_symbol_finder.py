import unittest, alpaca_request_methods
from unittest.mock import patch, MagicMock
from Finder.symbol_finder import (
    get_asset_price,
    get_list_of_tradeable_stocks,
    fetch_price_data_concurrently,
    sort_list_from_lowest_price_to_highest_price
)  


class TestAssetMethods(unittest.TestCase):

    @patch("alpaca_request_methods.get_alpaca_connection")
    def test_get_asset_price_success(self, mock_connection):
        """Test get_asset_price with a valid price."""
        mock_bar = MagicMock()
        mock_bar.c = "150.25"
        mock_connection.return_value.get_latest_bar.return_value = mock_bar

        price = get_asset_price("AAPL")
        self.assertEqual(price, 150.25)
        mock_connection.return_value.get_latest_bar.assert_called_once_with("AAPL")

    @patch("alpaca_request_methods.get_alpaca_connection")
    def test_get_asset_price_failure(self, mock_connection):
        """Test get_asset_price when an exception occurs."""
        mock_connection.return_value.get_latest_bar.side_effect = Exception("API Error")

        price = get_asset_price("AAPL")
        self.assertIsNone(price)

    @patch("alpaca_request_methods.get_alpaca_connection")
    def test_get_list_of_tradeable_stocks(self, mock_connection):
        """Test get_list_of_tradeable_stocks with valid exchanges."""
        mock_assets = [
            MagicMock(symbol="AAPL", exchange="NASDAQ"),
            MagicMock(symbol="MSFT", exchange="NYSE"),
            MagicMock(symbol="GOOGL", exchange="NASDAQ"),
        ]
        mock_connection.return_value.list_assets.return_value = mock_assets

        stocks = get_list_of_tradeable_stocks()
        self.assertIn("AAPL", stocks)
        self.assertIn("MSFT", stocks)
        self.assertNotIn("XYZ", stocks)

    @patch("Finder.symbol_finder.get_asset_price")
    def test_fetch_price_data_concurrently(self, mock_get_price):
        """Test fetch_price_data_concurrently with mock price data."""
        mock_get_price.side_effect = lambda symbol: 100 if symbol == "AAPL" else 50

        symbols = ["AAPL", "MSFT", "GOOGL"]
        result = fetch_price_data_concurrently(symbols, min_price=60, max_price=150)
        self.assertEqual(len(result), 1)  # Only AAPL is within the price range
        self.assertEqual(result[0][0], "AAPL")  # AAPL should be included

    def test_sort_list_from_lowest_price_to_highest_price(self):
        """Test sort_list_from_lowest_price_to_highest_price."""
        assets = [
            ["AAPL", 150.25],
            ["MSFT", 120.50],
            ["GOOGL", 200.75],
        ]
        sorted_assets = sort_list_from_lowest_price_to_highest_price(assets)
        self.assertEqual(sorted_assets[0][0], "MSFT")  # Lowest price first
        self.assertEqual(sorted_assets[-1][0], "GOOGL")  # Highest price last


if __name__ == "__main__":
    unittest.main()
