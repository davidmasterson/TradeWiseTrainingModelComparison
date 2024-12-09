import unittest, subprocess
from unittest.mock import patch, mock_open
from model_trainer_predictor_methods import stock_predictor_using_pretrained_model  
from flask import session, Flask


class TestStockPredictor(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open, read_data=(
        "symbol,purchase_date,purchase_price,sell_date,sell_price,days_to_sell,take_profit_price,"
        "stop_out_price,hit_take_profit,sector,SMA5_prob,SMA20_prob,SMA5_Slope_prob,SMA20_Slope_prob,"
        "open_mean,open_std,close_mean,close_std,SMA5_last,SMA20_last,SMA5_Slope_last,SMA20_Slope_last,"
        "symbol_encoded,purchase_date_encoded,sell_date_encoded,purchase_day,purchase_month,"
        "purchase_year,sell_day,sell_month,sell_year,hit_take_profit_predicted\n"
        "AAPL,2023-11-01,150.00,,200.00,10,155.00,145.00,1,Technology,0.8,0.75,0.9,0.85,120.0,"
        "15.0,130.0,16.0,151.0,152.0,0.01,0.02,1,20231101,20231102,1,11,2023,1,12,2023,1\n"
    ))
    @patch('subprocess.run')
    @patch('flask.session', {'user_id': 1})
    def test_stock_predictor_using_pretrained_model(self, mock_subprocess, mock_file):
        """Test the function with mocked subprocess and file handling."""
        mock_subprocess.return_value.returncode = 0  # Simulate successful subprocess execution

        # Call the function
        results = stock_predictor_using_pretrained_model()

        # Assertions
        self.assertEqual(len(results), 1)  # Ensure one result is processed
        result = results[0]

        # Validate the content of the result
        self.assertEqual(result[0], 'AAPL')  # Symbol
        self.assertEqual(result[1], '2023-11-01')  # Purchase date
        self.assertEqual(result[2], 150.00)  # Purchase price
        self.assertEqual(result[3], '')  # Sell date
        self.assertEqual(result[4], '200.00')  # Sell price
        self.assertEqual(result[31], 1)  # Predicted hit_take_profit

        # Validate the subprocess call
        mock_subprocess.assert_called_once_with(
            ['python3', 'Hypothetical_Predictor/future_predictor.py', '1']
        )

        # Validate file opening and reading
        mock_file.assert_called_once_with('Hypothetical_Predictor/future_predictions.csv', 'r')

    @patch('builtins.open', new_callable=mock_open, read_data="symbol,purchase_date,purchase_price\n")
    @patch('subprocess.run')
    @patch('flask.session', {'user_id': 1})
    def test_empty_predictions(self, mock_subprocess, mock_file):
        """Test with an empty CSV file."""
        mock_subprocess.return_value.returncode = 0  # Simulate successful subprocess execution

        # Call the function
        results = stock_predictor_using_pretrained_model()

        # Assertions
        self.assertEqual(len(results), 0)  # No results should be returned

        # Validate the subprocess call
        mock_subprocess.assert_called_once_with(
            ['python3', 'Hypothetical_Predictor/future_predictor.py', '1']
        )

    @patch('subprocess.run')
    def test_subprocess_failure(self, mock_subprocess):
        """Test subprocess failure."""
        # Mock the subprocess.run to raise an exception
        mock_subprocess.side_effect = Exception("Subprocess failed")

        # Create a Flask app context
        app = Flask(__name__)
        app.secret_key = 'test_secret_key'  # Set a secret key for the session

        with app.app_context():
            with app.test_request_context('/'):
                # Set the session data
                with patch.dict('flask.session', {'user_id': 1}):
                    # Call the function and ensure it handles the exception gracefully
                    with self.assertRaises(Exception):
                        stock_predictor_using_pretrained_model()

                    # Validate the subprocess call
                    mock_subprocess.assert_called_once_with(
                        ['python3', 'Hypothetical_Predictor/future_predictor.py', '1']
                    )


if __name__ == "__main__":
    unittest.main()
