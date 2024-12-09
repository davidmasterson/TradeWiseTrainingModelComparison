import unittest
from unittest.mock import patch, MagicMock
from datetime import date
from Models.manual_metrics import Manual_metrics, calculate_manual_metrics  # Assuming your module is named Models.manual_metrics


class TestManualMetrics(unittest.TestCase):

    def setUp(self):
        """Set up common variables for testing."""
        self.manual_metrics = Manual_metrics(
            accuracy=0.9,
            error_rate=0.1,
            cumulative_correct_predictions=90,
            cumulative_incorrect_predictions=10,
            time_to_close_correct_predictions=2,
            cumulative_profit=1000.0,
            cumulative_loss=200.0,
            sector_breakdown_profit={"tech": 500.0},
            sector_breakdown_loss={"finance": 100.0},
            sector_breakdown_rec={"energy": 300.0},
            date=date.today()
        )

    @patch("Models.manual_metrics.manual_metrics_DAOIMPL.get_manual_metrics_cumlative_correct_predictions")
    def test_calculate_manual_algo_cumulative_correct(self, mock_correct):
        """Test calculation of cumulative correct predictions."""
        mock_correct.return_value = 100
        result = Manual_metrics.calculate_manual_algo_cumulative_correct()
        self.assertEqual(result, 100)
        mock_correct.assert_called_once()

    @patch("Models.manual_metrics.manual_metrics_DAOIMPL.get_manual_metrics_cumlative_incorrect_predictions")
    def test_calculate_manual_algo_cumulative_incorrect(self, mock_incorrect):
        """Test calculation of cumulative incorrect predictions."""
        mock_incorrect.return_value = 20
        result = Manual_metrics.calculate_manual_algo_cumulative_incorrect()
        self.assertEqual(result, 20)
        mock_incorrect.assert_called_once()

    @patch("Models.manual_metrics.Manual_metrics.calculate_manual_algo_cumulative_correct")
    @patch("Models.manual_metrics.Manual_metrics.calculate_manual_algo_cumulative_incorrect")
    def test_calculate_manual_algo_accuracy_rate(self, mock_correct, mock_incorrect):
        """Test calculation of accuracy rate."""
        mock_correct.return_value = 90
        mock_incorrect.return_value = 10
        accuracy = Manual_metrics.calculate_manual_algo_accuracy_rate()
        self.assertEqual(accuracy, 0.9)
        mock_correct.assert_called_once()
        mock_incorrect.assert_called_once()

    @patch("Models.manual_metrics.Manual_metrics.calculate_manual_algo_accuracy_rate")
    def test_calculate_manual_algo_inaccuracy_rate(self, mock_accuracy):
        """Test calculation of inaccuracy rate."""
        mock_accuracy.return_value = 0.9
        inaccuracy = Manual_metrics.calculate_manual_algo_inaccuracy_rate()
        self.assertEqual(inaccuracy, 0.1)
        mock_accuracy.assert_called_once()

    @patch("Models.manual_metrics.manual_metrics_DAOIMPL.get_manual_metrics_cumlative_profits")
    def test_calculate_manual_algo_cumulative_profit(self, mock_profit):
        """Test calculation of cumulative profit."""
        mock_profit.return_value = 1500.0
        result = Manual_metrics.calculate_manual_algo_cumulative_profit()
        self.assertEqual(result, 1500.0)
        mock_profit.assert_called_once()

    @patch("Models.manual_metrics.manual_metrics_DAOIMPL.get_manual_metrics_cumlative_losses")
    def test_calculate_manual_algo_cumulative_loss(self, mock_loss):
        """Test calculation of cumulative loss."""
        mock_loss.return_value = 300.0
        result = Manual_metrics.calculate_manual_algo_cumulative_loss()
        self.assertEqual(result, 300.0)
        mock_loss.assert_called_once()

    @patch("Models.manual_metrics.transactions_DAOIMPL.select_manual_sector_profits_symbols")
    @patch("Models.manual_metrics.transaction.transaction.aggregate_sectors_for_stock_symbols")
    def test_get_sector_data_for_trained_model_profit(self, mock_aggregate, mock_select):
        """Test sector data aggregation for profit."""
        mock_select.return_value = ["AAPL", "GOOGL"]
        mock_aggregate.return_value = {"tech": 500.0}
        result = Manual_metrics.get_sector_data_for_trained_model_profit_loss_rec_and_notrec()
        self.assertEqual(result[0], '{"tech": 500.0}')
        mock_select.assert_called_once()
        mock_aggregate.assert_called_once_with(["AAPL", "GOOGL"])

    @patch("Models.manual_metrics.Manual_metrics.calculate_manual_algo_accuracy_rate")
    @patch("Models.manual_metrics.Manual_metrics.calculate_manual_algo_inaccuracy_rate")
    @patch("Models.manual_metrics.Manual_metrics.calculate_manual_algo_cumulative_correct")
    @patch("Models.manual_metrics.Manual_metrics.calculate_manual_algo_cumulative_incorrect")
    @patch("Models.manual_metrics.Manual_metrics.calculate_manual_algo_cumulative_profit")
    @patch("Models.manual_metrics.Manual_metrics.calculate_manual_algo_cumulative_loss")
    @patch("Models.manual_metrics.Manual_metrics.get_sector_data_for_trained_model_profit_loss_rec_and_notrec")
    def test_calculate_manual_metrics(
        self, mock_sectors, mock_loss, mock_profit, mock_incorrect, mock_correct, mock_inaccuracy, mock_accuracy
    ):
        """Test the overall manual metrics calculation."""
        mock_accuracy.return_value = 0.9
        mock_inaccuracy.return_value = 0.1
        mock_correct.return_value = 90
        mock_incorrect.return_value = 10
        mock_profit.return_value = 1000.0
        mock_loss.return_value = 200.0
        mock_sectors.return_value = [
            '{"tech": 500.0}',
            '{"finance": 100.0}',
            '{"energy": 300.0}',
        ]

        result = calculate_manual_metrics()
        self.assertEqual(result.accuracy, 0.9)
        self.assertEqual(result.error_rate, 0.1)
        self.assertEqual(result.cumulative_correct_predictions, 90)
        self.assertEqual(result.cumulative_incorrect_predictions, 10)
        self.assertEqual(result.cumulative_profit, 1000.0)
        self.assertEqual(result.cumulative_loss, 200.0)
        self.assertEqual(result.sector_breakdown_profit, '{"tech": 500.0}')
        self.assertEqual(result.sector_breakdown_loss, '{"finance": 100.0}')
        self.assertEqual(result.sector_breakdown_rec, '{"energy": 300.0}')


if __name__ == "__main__":
    unittest.main()
