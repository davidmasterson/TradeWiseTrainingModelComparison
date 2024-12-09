import unittest
from unittest.mock import patch, MagicMock
from datetime import date
from Models.metric import calculate_daily_metrics_values, Metric  

class TestCalculateDailyMetricsValues(unittest.TestCase):

    @patch("your_module.transactions_DAOIMPL")
    @patch("your_module.Metric.get_sector_data_for_trained_model_profit_loss_rec_and_notrec_for_user")
    def test_calculate_daily_metrics_values(self, mock_get_sector_data, mock_transactions_DAOIMPL):
        # Mock return values
        mock_transactions_DAOIMPL.calculate_correct_predictions_for_user.return_value = 8
        mock_transactions_DAOIMPL.calculate_incorrect_predictions_for_user.return_value = 2
        mock_transactions_DAOIMPL.calculate_average_days_to_close_for_user.return_value = 3.5
        mock_transactions_DAOIMPL.calculate_cumulative_loss_for_user.return_value = -200.0
        mock_transactions_DAOIMPL.calculate_cumulative_profit_for_user.return_value = 500.0

        mock_get_sector_data.return_value = ["{\"Tech\": 300.0}", "{\"Finance\": -200.0}"]

        # Call function
        user_id = 1
        metric = calculate_daily_metrics_values(user_id)

        # Assertions
        self.assertEqual(metric.accuracy, 0.8)
        self.assertEqual(metric.error_rate, 0.2)
        self.assertEqual(metric.cumulative_correct_predictions, 8)
        self.assertEqual(metric.cumulative_incorrect_predictions, 2)
        self.assertEqual(metric.time_to_close_correct_predictions, 3.5)
        self.assertEqual(metric.cumulative_profit, 500.0)
        self.assertEqual(metric.cumulative_loss, -200.0)
        self.assertEqual(metric.sector_breakdown_profit, "{\"Tech\": 300.0}")
        self.assertEqual(metric.sector_breakdown_loss, "{\"Finance\": -200.0}")
        self.assertEqual(metric.date, date.today())
        self.assertEqual(metric.user_id, user_id)

    @patch("your_module.metrics_DAOIMPL")
    @patch("your_module.plotters")
    def test_plot_model_metrics(self, mock_plotters, mock_metrics_DAOIMPL):
        # Mock return values
        mock_metrics_DAOIMPL.get_metrics_dates_by_user.return_value = [(date(2024, 12, 1),), (date(2024, 12, 2),)]
        mock_metrics_DAOIMPL.get_metrics_accuracies_for_user.return_value = [(0.8,), (0.85,)]
        mock_metrics_DAOIMPL.get_metrics_error_rates_for_user.return_value = [(0.2,), (0.15,)]
        mock_metrics_DAOIMPL.get_metrics_cumlative_correct_predictions_for_user.return_value = [(8,), (17,)]
        mock_metrics_DAOIMPL.get_metrics_cumlative_incorrect_predictions_for_user.return_value = [(2,), (3,)]
        mock_metrics_DAOIMPL.get_metrics_times_to_close_for_user.return_value = [(3.5,), (3.0,)]
        mock_metrics_DAOIMPL.get_metrics_cumlative_profits_for_user.return_value = [(500.0,), (800.0,)]
        mock_metrics_DAOIMPL.get_metrics_cumlative_losses_for_user.return_value = [(-200.0,), (-300.0,)]
        mock_metrics_DAOIMPL.get_all_last_sector_breakdowns_for_user.return_value = [
            "{\"Tech\": 300.0}",
            "{\"Finance\": -200.0}",
        ]

        # Call function
        user_id = 1
        Metric.plot_model_metrics(user_id)

        # Assertions
        mock_plotters.plot_accuracy.assert_called_once()
        mock_plotters.plot_error_rate.assert_called_once()
        mock_plotters.plot_cumulative_correct_predictions.assert_called_once()
        mock_plotters.plot_cumulative_incorrect_predictions.assert_called_once()
        mock_plotters.plot_time_to_close.assert_called_once()
        mock_plotters.plot_cumulative_profit.assert_called_once()
        mock_plotters.plot_cumulative_loss.assert_called_once()
        mock_plotters.plot_model_sector_breakdown_profits.assert_called_once_with("{\"Tech\": 300.0}", user_id)
        mock_plotters.plot_model_sector_breakdown_loss.assert_called_once_with("{\"Finance\": -200.0}", user_id)

    @patch("your_module.transactions_DAOIMPL")
    def test_get_sector_data(self, mock_transactions_DAOIMPL):
        # Mock return values
        mock_transactions_DAOIMPL.get_profit_sectors_for_user.return_value = {"Tech": 300.0}
        mock_transactions_DAOIMPL.get_loss_sectors_for_user.return_value = {"Finance": -200.0}

        # Call function
        user_id = 1
        sectors = Metric.get_sector_data_for_trained_model_profit_loss_rec_and_notrec_for_user(user_id)

        # Assertions
        self.assertEqual(sectors[0], "{\"Tech\": 300.0}")
        self.assertEqual(sectors[1], "{\"Finance\": -200.0}")

if __name__ == "__main__":
    unittest.main()
