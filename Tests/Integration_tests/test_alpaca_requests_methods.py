import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from unittest.mock import patch, MagicMock
from datetime import date, timedelta, datetime
import pandas as pd
from alpaca_request_methods import (
    get_alpaca_connection,
    get_alpaca_stream_connection,
    fetch_stock_data,
    get_symbol_current_price,
    connect_to_user_alpaca_account,
    create_alpaca_api_during_api_key_resub,
    create_alpaca_api,
    tradeapi,
    Stream
)  
from database import user_DAOIMPL, transactions_DAOIMPL


class TestAlpacaIntegration(unittest.TestCase):

    @patch("alpaca_request_methods.tradeapi.REST")
    def test_get_alpaca_connection(self, mock_rest):
        """Test get_alpaca_connection function."""
        mock_api = MagicMock()
        mock_rest.return_value = mock_api
        api = get_alpaca_connection()

        self.assertEqual(api, mock_api)
        mock_rest.assert_called_once()

    @patch("alpaca_request_methods.Stream")
    @patch("database.user_DAOIMPL.get_user_by_username")
    def test_get_alpaca_stream_connection(self, mock_get_user, mock_stream):
        """Test get_alpaca_stream_connection function."""
        mock_user = [{"alpaca_key": "key", "alpaca_secret": "secret", "alpaca_endpoint": "endpoint"}]
        mock_get_user.return_value = mock_user
        mock_conn = MagicMock()
        mock_stream.return_value = mock_conn

        conn = get_alpaca_stream_connection("test_user")

        self.assertEqual(conn, mock_conn)
        mock_get_user.assert_called_once_with("test_user")
        mock_stream.assert_called_once_with("key", "secret", base_url="endpoint")

    @patch("alpaca_request_methods.get_alpaca_connection")
    def test_get_symbol_current_price(self, mock_get_connection):
        """Test get_symbol_current_price function."""
        mock_api = MagicMock()
        mock_bar = MagicMock()
        mock_bar.c = 100.0
        mock_api.get_latest_bar.return_value = mock_bar
        mock_get_connection.return_value = mock_api

        price = get_symbol_current_price("AAPL")
        self.assertEqual(price, 100.0)

        mock_get_connection.assert_called_once()
        mock_api.get_latest_bar.assert_called_once_with("AAPL")
        mock_api.close.assert_called_once()

    @patch("alpaca_request_methods.get_alpaca_connection")
    def test_get_symbol_current_price_error(self, mock_get_connection):
        """Test get_symbol_current_price with an error."""
        mock_api = MagicMock()
        mock_api.get_latest_bar.side_effect = Exception("API error")
        mock_get_connection.return_value = mock_api

        price = get_symbol_current_price("AAPL")
        self.assertEqual(price, [])
        mock_get_connection.assert_called_once()
        mock_api.close.assert_called_once()

    @patch("alpaca_request_methods.tradeapi.REST")
    def test_create_alpaca_api_during_api_key_resub(self, mock_rest):
        """Test create_alpaca_api_during_api_key_resub function."""
        mock_api = MagicMock()
        mock_rest.return_value = mock_api

        api = create_alpaca_api_during_api_key_resub("key", "secret", "endpoint")
        self.assertEqual(api, mock_api)

        mock_rest.assert_called_once_with("key", "secret", "endpoint")

    @patch("alpaca_request_methods.tradeapi.REST")
    @patch("database.user_DAOIMPL.get_user_by_username")
    def test_create_alpaca_api(self, mock_get_user, mock_rest):
        """Test create_alpaca_api function."""
        mock_user = [{"alpaca_key": "key", "alpaca_secret": "secret", "alpaca_endpoint": "endpoint"}]
        mock_get_user.return_value = mock_user
        mock_api = MagicMock()
        mock_rest.return_value = mock_api

        api = create_alpaca_api("test_user")
        self.assertEqual(api, mock_api)

        mock_get_user.assert_called_once_with("test_user")
        mock_rest.assert_called_once_with("key", "secret", "endpoint")

    @patch("alpaca_request_methods.get_alpaca_connection")
    @patch("database.transactions_DAOIMPL.read_in_transactions")
    @patch("database.transactions_DAOIMPL.convert_lines_to_transaction_info_for_DF")
    def test_fetch_stock_data(self, mock_convert, mock_read, mock_get_connection):
        """Test fetch_stock_data function."""
        mock_api = MagicMock()
        mock_get_connection.return_value = mock_api

        mock_read.return_value = ([], [])
        mock_convert.return_value = [
            ["AAPL", date.today() - timedelta(days=365), 150, date.today(), 160, 10, 5, 200, 140, 1, "Technology"]
        ]
        mock_barset = MagicMock()
        mock_barset.c = 155.0
        mock_barset.o = 150.0
        mock_barset.t = datetime.now()
        mock_api.get_bars.return_value = [mock_barset]

        df_data = fetch_stock_data()

        self.assertIn("symbol", df_data)
        self.assertIn("historical_dates", df_data)

        mock_get_connection.assert_called_once()
        mock_read.assert_called_once()
        mock_convert.assert_called_once()
        mock_api.close.assert_called_once()

    def test_create_alpaca_api_during_api_key_resub_error(self):
        """Test create_alpaca_api_during_api_key_resub with an error."""
        with patch("alpaca_request_methods.tradeapi.REST", side_effect=Exception("API Error")):
            api = create_alpaca_api_during_api_key_resub("key", "secret", "endpoint")
            self.assertIsNone(api)


if __name__ == "__main__":
    unittest.main()
