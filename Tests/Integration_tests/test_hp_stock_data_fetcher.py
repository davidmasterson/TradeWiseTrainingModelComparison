import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from unittest.mock import patch, MagicMock
from Hypothetical_Predictor.stock_data_fetcher import fetch_stock_data  
from database import transactions_DAOIMPL
import sector_finder
import alpaca_request_methods

class TestFetchStockData(unittest.TestCase):

    @patch('database.transactions_DAOIMPL')
    @patch('.sector_finder')
    @patch('.alpaca_request_methods')
    def test_fetch_stock_data(self, mock_alpaca, mock_sector_finder, mock_transactions):
        """
        Test the fetch_stock_data function with mocked dependencies.
        """
        # Mock transaction data
        mock_transactions.read_in_transactions.return_value = (
            ['header'],  # Simulated header row
            [
                "AAPL,2023-11-01,150.00,N/A,N/A,N/A,N/A,155.00,145.00,1,N/A"
            ]  # Simulated transaction row
        )
        mock_transactions.convert_lines_to_transaction_info_for_DF.return_value = [
            ['AAPL', '2023-11-01', 150.00, 'N/A', 'N/A', 'N/A', 'N/A', 155.00, 145.00, 1]
        ]

        # Mock Alpaca connection
        mock_alpaca_connection = MagicMock()
        mock_alpaca_connection.get_bars.return_value = [
            MagicMock(t=MagicMock(year=2023, month=11, day=1), c=151.00, o=149.00)
        ]
        mock_alpaca.get_alpaca_connection.return_value = mock_alpaca_connection

        # Mock sector_finder
        mock_sector_finder.get_stock_sector.return_value = 'Technology'

        # Call the function
        result = fetch_stock_data(years=1)

        # Validate the data returned
        self.assertEqual(len(result['symbol']), 1)
        self.assertEqual(result['symbol'][0], 'AAPL')
        self.assertEqual(result['purchase_date'][0], '2023-11-01')
        self.assertEqual(result['sector'][0], 'Technology')
        self.assertEqual(result['close'][0][0], 151.00)  # Mocked close price
        self.assertEqual(result['open'][0][0], 149.00)  # Mocked open price

        # Validate the calls to mocked dependencies
        mock_transactions.read_in_transactions.assert_called_once_with('/Hypothetical_Predictor/transactions.csv')
        mock_sector_finder.get_stock_sector.assert_called_once_with('AAPL')
        mock_alpaca_connection.get_bars.assert_called_once_with(
            'AAPL', '1Day', start='2022-11-01', end='2023-11-01'
        )
        mock_alpaca_connection.close.assert_called_once()

    @patch('database.transactions_DAOIMPL')
    @patch('.alpaca_request_methods')
    def test_no_transactions(self, mock_alpaca, mock_transactions):
        """
        Test the fetch_stock_data function when there are no transactions.
        """
        # Mock transaction data to return no transactions
        mock_transactions.read_in_transactions.return_value = (['header'], [])
        mock_transactions.convert_lines_to_transaction_info_for_DF.return_value = []

        # Call the function
        result = fetch_stock_data(years=1)

        # Validate that the result is empty
        self.assertEqual(len(result['symbol']), 0)
        self.assertEqual(len(result['close']), 0)

        # Validate that Alpaca was not called
        mock_alpaca.get_alpaca_connection.assert_not_called()

    @patch('database.transactions_DAOIMPL')
    @patch('.alpaca_request_methods')
    def test_alpaca_connection_error(self, mock_alpaca, mock_transactions):
        """
        Test the fetch_stock_data function when Alpaca connection fails.
        """
        # Mock transaction data
        mock_transactions.read_in_transactions.return_value = (
            ['header'],
            [
                "AAPL,2023-11-01,150.00,N/A,N/A,N/A,N/A,155.00,145.00,1,N/A"
            ]
        )
        mock_transactions.convert_lines_to_transaction_info_for_DF.return_value = [
            ['AAPL', '2023-11-01', 150.00, 'N/A', 'N/A', 'N/A', 'N/A', 155.00, 145.00, 1]
        ]

        # Simulate Alpaca connection error
        mock_alpaca.get_alpaca_connection.side_effect = Exception("Connection error")

        # Call the function
        with self.assertLogs(level='INFO') as log:
            result = fetch_stock_data(years=1)

        # Validate the result is empty due to connection failure
        self.assertEqual(len(result['symbol']), 0)

        # Check the log for connection error message
        self.assertIn("Connection error", log.output[0])

    @patch('database.transactions_DAOIMPL')
    @patch('.alpaca_request_methods')
    def test_no_sector_info(self, mock_alpaca, mock_transactions,mock_sector_finder):
        """
        Test fetch_stock_data when sector information is not available.
        """
        # Mock transaction data
        mock_transactions.read_in_transactions.return_value = (
            ['header'],
            [
                "AAPL,2023-11-01,150.00,N/A,N/A,N/A,N/A,155.00,145.00,1,N/A"
            ]
        )
        mock_transactions.convert_lines_to_transaction_info_for_DF.return_value = [
            ['AAPL', '2023-11-01', 150.00, 'N/A', 'N/A', 'N/A', 'N/A', 155.00, 145.00, 1]
        ]

        # Mock Alpaca connection
        mock_alpaca_connection = MagicMock()
        mock_alpaca_connection.get_bars.return_value = [
            MagicMock(t=MagicMock(year=2023, month=11, day=1), c=151.00, o=149.00)
        ]
        mock_alpaca.get_alpaca_connection.return_value = mock_alpaca_connection

        # Simulate sector information missing
        mock_sector_finder.get_stock_sector.return_value = 'Sector not available'

        # Call the function
        result = fetch_stock_data(years=1)

        # Validate that 'Sector not available' is returned
        self.assertEqual(result['sector'][0], 'Sector not available')


if __name__ == "__main__":
    unittest.main()
