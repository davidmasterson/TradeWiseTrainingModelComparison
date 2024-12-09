import unittest
from unittest.mock import patch, MagicMock
from database import trade_settings_DAOIMPL, progression_DAOIMPL
from Finder import symbol_finder 
from Recommender import recommender
from Purchaser import score_based_purchaser, purchaser
from sector_finder import get_stock_company_name
from MachineLearningModels import manual_alg_requisition_script
from Purchaser.purchaser import get_and_set_progress, generate_recommendations_task
from Models import user 


class TestRecommendationSystem(unittest.TestCase):

    @patch("trade_settings_DAOIMPL.get_trade_settings_by_user")
    @patch("symbol_finder.get_list_of_tradeable_stocks")
    @patch("symbol_finder.fetch_price_data_concurrently")
    @patch("symbol_finder.sort_list_from_lowest_price_to_highest_price")
    @patch("recommender.get_model_recommendation")
    @patch("score_based_purchaser.process_symbols_for_purchase")
    @patch("sector_finder.get_stock_company_name")
    @patch("manual_alg_requisition_script.request_articles")
    @patch("manual_alg_requisition_script.process_phrase_for_sentiment")
    @patch("purchaser.get_and_set_progress")
    @patch("user.User.get_id")
    def test_generate_recommendations_task(
        self,
        mock_get_id,
        mock_get_and_set_progress,
        mock_process_phrase_for_sentiment,
        mock_request_articles,
        mock_get_stock_company_name,
        mock_process_symbols_for_purchase,
        mock_get_model_recommendation,
        mock_sort_list,
        mock_fetch_price_data,
        mock_get_tradeable_stocks,
        mock_get_trade_settings
    ):
        """Test the generate_recommendations_task function."""
        # Mock user ID and preferences
        mock_get_id.return_value = 1
        mock_get_trade_settings.return_value = (1, 2, 100, 500, None, 0.5, None, 5000)

        # Mock tradeable stocks and price data
        mock_get_tradeable_stocks.return_value = ["AAPL", "MSFT", "GOOG"]
        mock_fetch_price_data.return_value = [{"symbol": "AAPL", "price": 150}, {"symbol": "MSFT", "price": 300}]
        mock_sort_list.return_value = [{"symbol": "AAPL", "price": 150}, {"symbol": "MSFT", "price": 300}]

        # Mock model recommendations
        mock_get_model_recommendation.return_value = [{"symbol": "AAPL", "score": 0.9}, {"symbol": "MSFT", "score": 0.8}]

        # Mock purchase processing
        mock_process_symbols_for_purchase.return_value = {
            "AAPL": {"symbol": "AAPL", "sentiment": 0.6},
            "MSFT": {"symbol": "MSFT", "sentiment": 0.7},
        }

        # Mock sentiment processing
        mock_get_stock_company_name.side_effect = lambda x: f"{x} Corp"
        mock_request_articles.side_effect = lambda symbol, name: f"Articles for {symbol}"
        mock_process_phrase_for_sentiment.side_effect = lambda articles, name: 0.1

        # Call the function
        result = generate_recommendations_task(1)

        # Assertions
        self.assertEqual(len(result), 2)  # Both symbols meet the sentiment threshold
        mock_get_id.assert_called_once()
        mock_get_and_set_progress.assert_called_with(100)

    @patch("progression_DAOIMPL.get_recommender_progress")
    @patch("progression_DAOIMPL.update_recommender_progress")
    @patch("progression_DAOIMPL.insert_recommender_progress")
    def test_get_and_set_progress(self, mock_insert_progress, mock_update_progress, mock_get_progress):
        """Test the get_and_set_progress function."""
        # Simulate progress ID found
        mock_get_progress.return_value = (1, 50)
        get_and_set_progress(75)

        # Assert update was called
        mock_update_progress.assert_called_once_with(75, 1)
        mock_insert_progress.assert_not_called()

        # Simulate no progress found
        mock_get_progress.return_value = False
        get_and_set_progress(0)

        # Assert insert was called
        mock_insert_progress.assert_called_once_with(0)
        mock_update_progress.assert_called_once()  # Should not increment further


if __name__ == "__main__":
    unittest.main()
