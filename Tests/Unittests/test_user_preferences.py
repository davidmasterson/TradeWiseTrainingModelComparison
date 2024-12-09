import unittest
from Models.user_preferences import UserPreferences  


class TestUserPreferences(unittest.TestCase):

    def setUp(self):
        """Set up a sample UserPreferences instance."""
        self.min_investment = 500.0
        self.max_investment = 10000.0
        self.min_price_per_share = 10.0
        self.max_price_per_share = 500.0
        self.user_id = 1
        self.risk_tolerance = 0.5

        self.user_preferences = UserPreferences(
            self.min_investment,
            self.max_investment,
            self.min_price_per_share,
            self.max_price_per_share,
            self.user_id,
            self.risk_tolerance
        )

    def test_initialization(self):
        """Test that UserPreferences initializes correctly."""
        self.assertEqual(self.user_preferences.min_investment, self.min_investment)
        self.assertEqual(self.user_preferences.max_investment, self.max_investment)
        self.assertEqual(self.user_preferences.min_price_per_share, self.min_price_per_share)
        self.assertEqual(self.user_preferences.max_price_per_share, self.max_price_per_share)
        self.assertEqual(self.user_preferences.user_id, self.user_id)
        self.assertEqual(self.user_preferences.risk_tolerance, self.risk_tolerance)

    def test_attribute_types(self):
        """Test that all attributes have the correct types."""
        self.assertIsInstance(self.user_preferences.min_investment, float)
        self.assertIsInstance(self.user_preferences.max_investment, float)
        self.assertIsInstance(self.user_preferences.min_price_per_share, float)
        self.assertIsInstance(self.user_preferences.max_price_per_share, float)
        self.assertIsInstance(self.user_preferences.user_id, int)
        self.assertIsInstance(self.user_preferences.risk_tolerance, float)


if __name__ == "__main__":
    unittest.main()
