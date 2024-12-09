import unittest
from unittest.mock import patch, MagicMock
from Models.recommended import Recommended 
from sector_finder import get_stock_sector 


class TestRecommended(unittest.TestCase):
    
    @patch("sector_finder.get_stock_sector")
    def test_initialization(self, mock_get_stock_sector):
        """Test that Recommended initializes correctly and calls get_stock_sector."""
        mock_get_stock_sector.return_value = "Technology"

        symbol = "AAPL"
        price = 150.0
        confidence = 0.9
        user_id = 1

        recommended_instance = Recommended(symbol, price, confidence, user_id)

        # Assert initialization
        self.assertEqual(recommended_instance.symbol, symbol)
        self.assertEqual(recommended_instance.price, price)
        self.assertEqual(recommended_instance.confidence, confidence)
        self.assertEqual(recommended_instance.user_id, user_id)
        self.assertEqual(recommended_instance.sector, "Technology")

        # Ensure get_stock_sector was called with the correct symbol
        mock_get_stock_sector.assert_called_once_with(symbol)

    @patch("sector_finder.get_stock_sector")
    def test_get_stock_sector_failure(self, mock_get_stock_sector):
        """Test behavior when get_stock_sector fails."""
        mock_get_stock_sector.side_effect = Exception("Failed to fetch sector")

        symbol = "AAPL"
        price = 150.0
        confidence = 0.9
        user_id = 1

        with self.assertRaises(Exception) as context:
            Recommended(symbol, price, confidence, user_id)

        self.assertEqual(str(context.exception), "Failed to fetch sector")
        mock_get_stock_sector.assert_called_once_with(symbol)


if __name__ == "__main__":
    unittest.main()
