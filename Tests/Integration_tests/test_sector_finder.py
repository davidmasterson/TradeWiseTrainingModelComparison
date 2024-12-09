import unittest
from unittest.mock import patch, MagicMock
from sector_finder import get_stock_sector, get_stock_company_name, yf  


class TestStockSectorFinder(unittest.TestCase):

    @patch("yf.Ticker")
    def test_get_stock_sector_success(self, mock_ticker):
        """Test get_stock_sector with a valid sector."""
        mock_info = {"sector": "Technology"}
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = mock_info
        mock_ticker.return_value = mock_ticker_instance

        sector = get_stock_sector("AAPL")
        self.assertEqual(sector, "Technology")
        mock_ticker.assert_called_once_with("AAPL")

    @patch("yf.Ticker")
    def test_get_stock_sector_no_sector(self, mock_ticker):
        """Test get_stock_sector when sector is not available."""
        mock_info = {}
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = mock_info
        mock_ticker.return_value = mock_ticker_instance

        sector = get_stock_sector("AAPL")
        self.assertEqual(sector, "Sector not available")
        mock_ticker.assert_called_once_with("AAPL")

    @patch("yf.Ticker")
    def test_get_stock_company_name_with_type(self, mock_ticker):
        """Test get_stock_company_name with company types (Inc., LLC., DBA.)."""
        mock_info = {"shortName": "Apple Inc."}
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = mock_info
        mock_ticker.return_value = mock_ticker_instance

        company_name = get_stock_company_name("AAPL")
        self.assertEqual(company_name, "apple")
        mock_ticker.assert_called_once_with("AAPL")

    @patch("yf.Ticker")
    def test_get_stock_company_name_no_type(self, mock_ticker):
        """Test get_stock_company_name without company types."""
        mock_info = {"shortName": "Microsoft"}
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = mock_info
        mock_ticker.return_value = mock_ticker_instance

        company_name = get_stock_company_name("MSFT")
        self.assertEqual(company_name, "microsoft")
        mock_ticker.assert_called_once_with("MSFT")

    @patch("yf.Ticker")
    def test_get_stock_company_name_exception(self, mock_ticker):
        """Test get_stock_company_name when an exception occurs."""
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = {}
        mock_ticker.return_value = mock_ticker_instance
        mock_ticker.side_effect = Exception("Error fetching stock info")

        company_name = get_stock_company_name("XYZ")
        self.assertEqual(company_name, "xyz")
        mock_ticker.assert_called_once_with("XYZ")


if __name__ == "__main__":
    unittest.main()
