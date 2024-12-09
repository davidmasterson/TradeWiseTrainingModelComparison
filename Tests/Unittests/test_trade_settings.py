import unittest
from Models.trade_setting import TradeSetting  


class TestTradeSetting(unittest.TestCase):

    def setUp(self):
        """Set up a sample TradeSetting instance."""
        self.user_id = 1
        self.min_price = 10.0
        self.max_price = 100.0
        self.risk_tolerance = 0.2
        self.confidence_threshold = 0.85
        self.min_total = 1000.0
        self.max_total = 10000.0

        self.trade_setting = TradeSetting(
            self.user_id,
            self.min_price,
            self.max_price,
            self.risk_tolerance,
            self.confidence_threshold,
            self.min_total,
            self.max_total
        )

    def test_initialization(self):
        """Test that TradeSetting initializes correctly."""
        self.assertEqual(self.trade_setting.user_id, self.user_id)
        self.assertEqual(self.trade_setting.min_price, self.min_price)
        self.assertEqual(self.trade_setting.max_price, self.max_price)
        self.assertEqual(self.trade_setting.risk_tolerance, self.risk_tolerance)
        self.assertEqual(self.trade_setting.confidence_threshold, self.confidence_threshold)
        self.assertEqual(self.trade_setting.min_total, self.min_total)
        self.assertEqual(self.trade_setting.max_total, self.max_total)

    def test_attribute_types(self):
        """Test that all attributes have the correct types."""
        self.assertIsInstance(self.trade_setting.user_id, int)
        self.assertIsInstance(self.trade_setting.min_price, float)
        self.assertIsInstance(self.trade_setting.max_price, float)
        self.assertIsInstance(self.trade_setting.risk_tolerance, float)
        self.assertIsInstance(self.trade_setting.confidence_threshold, float)
        self.assertIsInstance(self.trade_setting.min_total, float)
        self.assertIsInstance(self.trade_setting.max_total, float)


if __name__ == "__main__":
    unittest.main()
