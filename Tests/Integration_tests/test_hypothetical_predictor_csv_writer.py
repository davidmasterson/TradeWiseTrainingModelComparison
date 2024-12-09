import unittest, alpaca_request_methods
from unittest.mock import patch, mock_open
from datetime import date
from Hypothetical_Predictor import CSV_Writer  

class TestCSVWriter(unittest.TestCase):

    @patch("alpaca_request_methods.get_symbol_current_price")
    @patch("builtins.open", new_callable=mock_open)
    def test_write_temporary_csv_with_string_symbols(self, mock_file, mock_get_price):
        """Test CSV writing with a list of string symbols."""
        mock_get_price.return_value = 100.0
        symbols = ["AAPL", "MSFT", "GOOGL"]
        
        CSV_Writer.write_temporary_csv(symbols)
        
        mock_file.assert_called_once_with('/home/ubuntu/TradeWiseTrainingModelComparison/Hypothetical_Predictor/transactions.csv', 'w')
        handle = mock_file()
        expected_calls = [
            f"0,AAPL,{date.today()},100.0,1,100.0,,,,N/A,N/A,N/A,N/A,3.0,0.0,N/A,103.0,99.0\n",
            f"1,MSFT,{date.today()},100.0,1,100.0,,,,N/A,N/A,N/A,N/A,3.0,0.0,N/A,103.0,99.0\n",
            f"2,GOOGL,{date.today()},100.0,1,100.0,,,,N/A,N/A,N/A,N/A,3.0,0.0,N/A,103.0,99.0\n",
        ]
        handle.write.assert_any_call(f"id,symbol,dp,ppps,qty,total_buy,pstring,ds,spps,tsp,sstring,expected,proi,actual,tp1,sop,result,user_id,processed\n")
        handle.write.assert_any_call(expected_calls[0])
        handle.write.assert_any_call(expected_calls[1])
        handle.write.assert_any_call(expected_calls[2])

    @patch("alpaca_request_methods.get_symbol_current_price")
    @patch("builtins.open", new_callable=mock_open)
    def test_write_temporary_csv_with_tuples(self, mock_file, mock_get_price):
        """Test CSV writing with a list of tuple symbols (symbol and price)."""
        mock_get_price.return_value = 100.0  # Default mock value, should not be used for tuples
        symbols = [("AAPL", 150.0), ("MSFT", 200.0)]
        
        CSV_Writer.write_temporary_csv(symbols)
        
        mock_file.assert_called_once_with('/home/ubuntu/TradeWiseTrainingModelComparison/Hypothetical_Predictor/transactions.csv', 'w')
        handle = mock_file()
        expected_calls = [
            f"0,AAPL,{date.today()},150.0,1,150.0,,,,N/A,N/A,N/A,N/A,4.5,0.0,N/A,154.5,148.5\n",
            f"1,MSFT,{date.today()},200.0,1,200.0,,,,N/A,N/A,N/A,N/A,6.0,0.0,N/A,206.0,198.0\n",
        ]
        handle.write.assert_any_call(f"id,symbol,dp,ppps,qty,total_buy,pstring,ds,spps,tsp,sstring,expected,proi,actual,tp1,sop,result,user_id,processed\n")
        handle.write.assert_any_call(expected_calls[0])
        handle.write.assert_any_call(expected_calls[1])

    @patch("alpaca_request_methods.get_symbol_current_price")
    @patch("builtins.open", new_callable=mock_open)
    def test_write_temporary_csv_with_mixed_symbols(self, mock_file, mock_get_price):
        """Test CSV writing with a mix of string and tuple symbols."""
        mock_get_price.side_effect = lambda symbol: 100.0 if isinstance(symbol, str) else None
        symbols = ["AAPL", ("MSFT", 200.0)]
        
        CSV_Writer.write_temporary_csv(symbols)
        
        mock_file.assert_called_once_with('/home/ubuntu/TradeWiseTrainingModelComparison/Hypothetical_Predictor/transactions.csv', 'w')
        handle = mock_file()
        expected_calls = [
            f"0,AAPL,{date.today()},100.0,1,100.0,,,,N/A,N/A,N/A,N/A,3.0,0.0,N/A,103.0,99.0\n",
            f"1,MSFT,{date.today()},200.0,1,200.0,,,,N/A,N/A,N/A,N/A,6.0,0.0,N/A,206.0,198.0\n",
        ]
        handle.write.assert_any_call(f"id,symbol,dp,ppps,qty,total_buy,pstring,ds,spps,tsp,sstring,expected,proi,actual,tp1,sop,result,user_id,processed\n")
        handle.write.assert_any_call(expected_calls[0])
        handle.write.assert_any_call(expected_calls[1])

if __name__ == "__main__":
    unittest.main()
