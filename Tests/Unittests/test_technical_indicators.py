import unittest
import pandas as pd
import numpy as np
from Models.technical_indicators import (
    calculate_rsi,
    calculate_sma,
    calculate_ema,
    calculate_momentum,
    prepare_data_with_indicators_and_target
)  


class TestIndicatorsAndDataPreparation(unittest.TestCase):

    def setUp(self):
        """Set up a synthetic dataset for testing."""
        self.df = pd.DataFrame({
            "open": np.linspace(100, 200, 100),
            "high": np.linspace(105, 210, 100),
            "low": np.linspace(95, 190, 100),
            "close": np.linspace(100, 200, 100),
            "volume": np.random.randint(1000, 10000, 100)
        })

    def test_calculate_rsi(self):
        """Test the calculation of RSI."""
        rsi = calculate_rsi(self.df["close"], window=14)
        self.assertEqual(len(rsi), len(self.df))
        self.assertFalse(rsi.isna().all())  # Ensure RSI values are calculated

    def test_calculate_sma(self):
        """Test the calculation of SMA."""
        sma = calculate_sma(self.df["close"], window=20)
        self.assertEqual(len(sma), len(self.df))
        self.assertTrue(sma.isna().sum() > 0)  # SMA should have NaN at the beginning

    def test_calculate_ema(self):
        """Test the calculation of EMA."""
        ema = calculate_ema(self.df["close"], span=20)
        self.assertEqual(len(ema), len(self.df))
        self.assertFalse(ema.isna().all())  # Ensure EMA values are calculated

    def test_calculate_momentum(self):
        """Test the calculation of Momentum."""
        momentum = calculate_momentum(self.df["close"], period=10)
        self.assertEqual(len(momentum), len(self.df))
        self.assertTrue(momentum.isna().sum() > 0)  # Momentum should have NaN at the beginning

    def test_prepare_data_with_indicators_and_target(self):
        """Test the data preparation function with indicators and targets."""
        time_steps = 30
        target_horizon = 12
        target_increase = 0.05
        
        X, y, scaler = prepare_data_with_indicators_and_target(self.df, time_steps, target_horizon, target_increase)

        # Assert the shapes of X and y
        self.assertEqual(X.shape[1], time_steps)  # Ensure the time_steps dimension is correct
        self.assertEqual(X.shape[0], len(y))  # Ensure number of samples matches

        # Assert y contains binary values
        self.assertTrue(np.array_equal(np.unique(y), [0, 1]) or np.array_equal(np.unique(y), [0]) or np.array_equal(np.unique(y), [1]))

        # Assert scaler is fitted
        self.assertIsNotNone(scaler)

        # Assert no NaN values in X
        self.assertFalse(np.isnan(X).any())

        # Assert y has no NaN values
        self.assertFalse(np.isnan(y).any())


if __name__ == "__main__":
    unittest.main()
