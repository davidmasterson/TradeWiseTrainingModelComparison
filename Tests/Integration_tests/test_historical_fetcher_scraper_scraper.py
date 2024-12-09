import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from HistoricalFetcherAndScraper.scraper import (
    search,
    scrape_article,
    get_sentiment_scores,
    filter_results_by_date,
    get_sa,
    
)  
from database import user_DAOIMPL
from MachineLearningModels import manual_alg_requisition_script


class TestSentimentAnalysis(unittest.TestCase):

    @patch("database.user_DAOIMPL.get_user_by_user_id")
    @patch("requests.get")
    def test_search_success(self, mock_get, mock_get_user):
        """Test search API call with valid inputs."""
        mock_response = MagicMock()
        mock_response.text = '{"news": [{"summary": "Positive news about the stock"}]}'
        mock_get.return_value = mock_response
        mock_get_user.return_value = [None, None, None, None, None, None, "test_key", "test_secret"]

        result = search(datetime.now(), "AAPL", 1)
        self.assertIn("Positive news", result)

    @patch("requests.get")
    def test_scrape_article_success(self, mock_get):
        """Test scrape_article with valid URL."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body><p>Test article content</p></body></html>"
        mock_get.return_value = mock_response

        content = scrape_article("http://example.com")
        self.assertIn("Test article content", content)

    @patch("requests.get")
    def test_scrape_article_failure(self, mock_get):
        """Test scrape_article with invalid URL."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        content = scrape_article("http://example.com")
        self.assertIsNone(content)

    def test_get_sentiment_scores(self):
        """Test get_sentiment_scores with sample text."""
        text = "This is a good day. Stocks are performing well."
        neg, neu, pos = get_sentiment_scores(text)
        self.assertGreater(pos, neg)
        self.assertGreater(neu, 0)

    @patch("requests.get")
    def test_filter_results_by_date(self, mock_get):
        """Test filter_results_by_date with mock responses."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Sample content with date February 20, 2023"
        mock_get.return_value = mock_response

        links = ["http://example1.com", "http://example2.com"]
        filtered_links, _ = filter_results_by_date(links, "February 20, 2023")
        self.assertIn("http://example1.com", filtered_links)

    @patch("HistoricalFetcherAndScraper.scraper.search")
    @patch("MachineLearningModels.manual_alg_requisition_script.process_phrase_for_sentiment")
    def test_get_sa(self, mock_process_phrase_for_sentiment, mock_search):
        """Test get_sa with mock response and sentiment analysis."""
        mock_search.return_value = '{"news": [{"summary": "Positive market updates"}]}'
        mock_process_phrase_for_sentiment.return_value = (10, 20, 70)

        sa_neu, sa_pos, sa_neg = get_sa(datetime.now(), "AAPL", 1)
        self.assertEqual(sa_neu, 10)
        self.assertEqual(sa_pos, 20)
        self.assertEqual(sa_neg, 70)


if __name__ == "__main__":
    unittest.main()
