import unittest
from unittest.mock import patch, MagicMock
from database import transactions_DAOIMPL
from datetime import date, datetime
from Models.transaction import transaction
import sector_finder 
from MachineLearningModels import manual_alg_requisition_script 


class TestTransaction(unittest.TestCase):
    
    @patch("sector_finder.get_stock_sector")
    def test_transaction_initialization(self, mock_get_stock_sector):
        """Test that transaction initializes correctly."""
        mock_get_stock_sector.return_value = "Technology"
        
        # Initialize a transaction
        tran = transaction(
            symbol="AAPL",
            dp=date.today(),
            ppps=150.0,
            qty=10,
            total_buy=1500.0,
            pstring="test_purchase_string",
            user_id=1
        )
        
        # Assert initialization
        self.assertEqual(tran.symbol, "AAPL")
        self.assertEqual(tran.dp, date.today())
        self.assertEqual(tran.ppps, 150.0)
        self.assertEqual(tran.qty, 10)
        self.assertEqual(tran.total_buy, 1500.0)
        self.assertEqual(tran.pstring, "test_purchase_string")
        self.assertEqual(tran.user_id, 1)
        self.assertEqual(tran.sector, "Technology")

        # Assert that the sector was fetched for the symbol
        mock_get_stock_sector.assert_called_once_with("AAPL")

    @patch("sector_finder.get_stock_sector")
    def test_aggregate_sectors_for_stock_symbols(self, mock_get_stock_sector):
        """Test sector aggregation for stock symbols."""
        mock_get_stock_sector.side_effect = ["Technology", "Finance", "Technology"]

        symbols = [("AAPL",), ("JPM",), ("GOOG",)]
        result = transaction.aggregate_sectors_for_stock_symbols(symbols)

        # Assert sector aggregation
        self.assertEqual(result, {"Technology": 2, "Finance": 1})
        self.assertEqual(mock_get_stock_sector.call_count, 3)

    @patch("manual_alg_requisition_script.request_articles")
    @patch("manual_alg_requisition_script.process_phrase_for_sentiment")
    def test_calculate_sentiment(self, mock_process_phrase_for_sentiment, mock_request_articles):
        """Test sentiment calculation."""
        mock_request_articles.return_value = "Mocked article content"
        mock_process_phrase_for_sentiment.return_value = (0.5, 0.3, 0.2)

        avg_neut, avg_pos, avg_neg = transaction.calculate_sentiment("AAPL")

        # Assert sentiment values
        self.assertEqual(avg_neut, 0.5)
        self.assertEqual(avg_pos, 0.3)
        self.assertEqual(avg_neg, 0.2)

        # Assert mocked calls
        mock_request_articles.assert_called_once_with("AAPL")
        mock_process_phrase_for_sentiment.assert_called_once_with("Mocked article content")

    @patch("transactions_DAOIMPL.initial_model_creation_trans_insert")
    def test_create_a_base_no_loss_or_gain_transaction(self, mock_initial_model_creation_trans_insert):
        """Test creation of a base no-loss-or-gain transaction."""
        mock_initial_model_creation_trans_insert.return_value = True

        result = transaction.create_a_base_no_loss_or_gain_transaction(user_id=1)

        # Assert transaction creation
        self.assertTrue(result)
        mock_initial_model_creation_trans_insert.assert_called_once()
        args, _ = mock_initial_model_creation_trans_insert.call_args
        new_transaction = args[0]
        
        self.assertEqual(new_transaction.symbol, "GTI")
        self.assertEqual(new_transaction.qty, 1)
        self.assertEqual(new_transaction.ppps, 0.01)
        self.assertEqual(new_transaction.total_buy, 0.01)
        self.assertEqual(new_transaction.result, "profit")


if __name__ == "__main__":
    unittest.main()
