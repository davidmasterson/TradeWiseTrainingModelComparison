import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from Seller.tasks import check_positions_for_user, monitor_all_users  
from database import transactions_DAOIMPL, database_connection_utility, user_DAOIMPL
import time
from concurrent.futures import ThreadPoolExecutor
import order_methods


class TestWebsocketScript(unittest.TestCase):

    @patch("alpaca_request_methods.create_alpaca_api")
    @patch("transactions_DAOIMPL.get_open_transactions_for_user_by_symbol_with_db_conn")
    @patch("order_methods.place_sell_order")
    @patch("database_connection_utility.get_db_connection")
    @patch("time.sleep", return_value=None)  # Mock sleep to avoid delays in testing
    def test_check_positions_for_user(
        self, mock_sleep, mock_get_db_connection, mock_place_sell_order, mock_get_open_transactions, mock_create_alpaca_api
    ):
        """Test the check_positions_for_user function."""
        # Mock database connection
        mock_db_conn = MagicMock()
        mock_get_db_connection.return_value = mock_db_conn

        # Mock Alpaca API
        mock_connection = MagicMock()
        mock_create_alpaca_api.return_value = mock_connection

        # Mock positions
        mock_connection.list_positions.return_value = [
            MagicMock(symbol="AAPL", current_price=150.0),
            MagicMock(symbol="MSFT", current_price=300.0),
        ]

        # Mock transactions
        mock_get_open_transactions.return_value = [
            (1, "AAPL", 10, 100, 2, None, "buy_string", None, None, None, None, None, None, None, 160.0, 140.0),
            (2, "MSFT", 5, 200, 1, None, "buy_string", None, None, None, None, None, None, None, 310.0, 290.0),
        ]

        # Call the function
        check_positions_for_user("test_user", 1)

        # Assertions
        mock_create_alpaca_api.assert_called_once_with("test_user")
        mock_get_open_transactions.assert_any_call("AAPL", 1, mock_db_conn)
        mock_place_sell_order.assert_any_call("AAPL", 2, 150.0, "test_user", "buy_string", 1)
        mock_place_sell_order.assert_any_call("MSFT", 1, 300.0, "test_user", "buy_string", 1)

        mock_db_conn.close.assert_called_once()

    @patch("user_DAOIMPL.get_all_users")
    @patch("Seller.tasks.check_positions_for_user")
    @patch("concurrent.futures.ThreadPoolExecutor")
    def test_monitor_all_users(self, mock_thread_pool, mock_check_positions, mock_get_all_users):
        """Test the monitor_all_users function."""
        # Mock users
        mock_get_all_users.return_value = [
            {"user_name": "user1", "id": 1},
            {"user_name": "user2", "id": 2},
        ]

        # Mock thread pool behavior
        mock_executor = MagicMock()
        mock_thread_pool.return_value.__enter__.return_value = mock_executor

        # Call the function
        monitor_all_users()

        # Assertions
        mock_get_all_users.assert_called_once()
        mock_executor.submit.assert_any_call(check_positions_for_user, "user1", 1)
        mock_executor.submit.assert_any_call(check_positions_for_user, "user2", 2)

        # Verify that all threads were submitted
        self.assertEqual(mock_executor.submit.call_count, 2)


if __name__ == "__main__":
    unittest.main()
