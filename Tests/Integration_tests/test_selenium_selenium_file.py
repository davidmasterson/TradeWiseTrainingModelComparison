import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from Selenium.selenium_file import (
    get_historical_stock_specific_sentiment_scores,
    get_historical_political_sentiment_scores,
    normalize_and_percentage,
)
from Selenium.selenium_file import webdriver,requests
from sector_finder import get_stock_company_name
from MachineLearningModels import manual_alg_requisition_script

class TestSentimentFunctions(unittest.TestCase):

    @patch("webdriver.Chrome")
    @patch("sector_finder.get_stock_company_name")
    @patch("manual_alg_requisition_script.process_phrase_for_sentiment")
    def test_get_historical_stock_specific_sentiment_scores(
        self, mock_process_sentiment, mock_get_company_name, mock_webdriver
    ):
        """Test get_historical_stock_specific_sentiment_scores."""
        mock_driver_instance = MagicMock()
        mock_webdriver.return_value = mock_driver_instance

        # Mock get_stock_company_name
        mock_get_company_name.return_value = "Test Company"

        # Mock process_phrase_for_sentiment
        mock_process_sentiment.return_value = (50, 30, 20)

        # Call the function
        sentiment, headings = get_historical_stock_specific_sentiment_scores("AAPL", datetime(2023, 11, 10))

        # Assertions
        self.assertEqual(sentiment, [50, 30, 20])
        self.assertIsInstance(headings, list)

        # Verify method calls
        mock_get_company_name.assert_called_once_with("AAPL")
        mock_process_sentiment.assert_called_once()

    @patch("requests.get")
    @patch("manual_alg_requisition_script.process_phrase_for_sentiment")
    def test_get_historical_political_sentiment_scores(
        self, mock_process_sentiment, mock_requests_get
    ):
        """Test get_historical_political_sentiment_scores."""
        # Mock the Wikipedia response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = "<html><div id='2023_November_10'><ul><li>Event 1</li><li>Event 2</li></ul></div></html>"
        mock_requests_get.return_value = mock_response

        # Mock sentiment processing
        mock_process_sentiment.return_value = (40, 30, 30)

        # Call the function
        sentiment, articles = get_historical_political_sentiment_scores(datetime(2023, 11, 10))

        # Assertions
        self.assertEqual(sentiment, [40, 30, 30])
        self.assertIn("Event 1", articles)
        self.assertIn("Event 2", articles)

        # Verify method calls
        mock_requests_get.assert_called_once()
        mock_process_sentiment.assert_called_once()

    def test_normalize_and_percentage(self):
        """Test normalize_and_percentage function."""
        # Case 1: Normal case
        pol_neu, pol_pos, pol_neg = normalize_and_percentage(50, 30, 20)
        self.assertEqual((pol_neu, pol_pos, pol_neg), (50, 30, 20))

        # Case 2: Zero total
        pol_neu, pol_pos, pol_neg = normalize_and_percentage(0, 0, 0)
        self.assertEqual((pol_neu, pol_pos, pol_neg), (0, 0, 0))

        # Case 3: Uneven distribution
        pol_neu, pol_pos, pol_neg = normalize_and_percentage(3, 2, 1)
        self.assertEqual(sum([pol_neu, pol_pos, pol_neg]), 100)

        # Case 4: All equal
        pol_neu, pol_pos, pol_neg = normalize_and_percentage(1, 1, 1)
        self.assertEqual(sum([pol_neu, pol_pos, pol_neg]), 100)


if __name__ == "__main__":
    unittest.main()
