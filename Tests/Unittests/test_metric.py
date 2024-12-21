import unittest
from unittest.mock import patch, MagicMock
from datetime import date
import Models
import Models.metric
import Models.plotters
import database
import database.metrics_DAOIMPL 

class TestCalculateDailyMetricsValues(unittest.TestCase):

    @patch("database.transactions_DAOIMPL")
    @patch("Models.metric.Metric.get_sector_data_for_trained_model_profit_loss_rec_and_notrec_for_user")
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
        metric = Models.metric.Metric(.8,.2,8,2,3.5,500.00,-200.00,"{\"Tech\": 300.0}","{\"Finance\": -200.0}",date.today(),1)
        print(metric.accuracy, metric.cumulative_correct_predictions, metric.cumulative_incorrect_predictions)

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

    
    @patch("database.transactions_DAOIMPL")
    def test_get_sector_data(self, mock_transactions_DAOIMPL):
        # Mock return values
        metric = Models.metric.Metric(.8,.2,8,2,3.5,500.00,-200.00,"{\"Tech\": 300.0}","{\"Finance\": -200.0}",date.today(),1)
        mock_transactions_DAOIMPL.get_profit_sectors_for_user.return_value = {"Tech": 300.0}
        mock_transactions_DAOIMPL.get_loss_sectors_for_user.return_value = {"Finance": -200.0}

        # Assertions
        self.assertEqual(metric.sector_breakdown_profit, "{\"Tech\": 300.0}")
        self.assertEqual(metric.sector_breakdown_loss, "{\"Finance\": -200.0}")

if __name__ == "__main__":
    unittest.main()
