import unittest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime
from Models.plotters import (  
    plot_accuracy,
    plot_error_rate,
    plot_cumulative_correct_predictions,
    plot_cumulative_incorrect_predictions,
    plot_time_to_close,
    plot_cumulative_profit,
    plot_cumulative_loss,
    plot_model_sector_breakdown_profits,
    plot_model_sector_breakdown_loss,
    generate_model_performance_graph,
)
from Models import plotters


class TestPlottingFunctions(unittest.TestCase):
    @patch("Models.plotters.plt.savefig")
    @patch("Models.plotters.plt.figure")
    def test_plot_accuracy(self, mock_figure, mock_savefig):
        accuracy_values = [85, 90, 95]
        time_periods = [datetime(2024, 12, 5), datetime(2024, 12, 6), datetime(2024, 12, 7)]
        user_id = 1

        plot_accuracy(accuracy_values, time_periods, user_id)

        mock_figure.assert_called_once_with(figsize=(8, 5))
        mock_savefig.assert_called_once_with(f'static/plots/model_accuracy_{user_id}.png')

    @patch("Models.plotters.plt.savefig")
    @patch("Models.plotters.plt.figure")
    def test_plot_error_rate(self, mock_figure, mock_savefig):
        error_rate_values = [15, 10, 5]
        time_periods = [datetime(2024, 12, 5), datetime(2024, 12, 6), datetime(2024, 12, 7)]
        user_id = 1

        plot_error_rate(error_rate_values, time_periods, user_id)

        mock_figure.assert_called_once_with(figsize=(8, 5))
        mock_savefig.assert_called_once_with(f'static/plots/model_error_rate_{user_id}.png')

    @patch("Models.plotters.plt.savefig")
    @patch("Models.plotters.plt.figure")
    def test_plot_cumulative_correct_predictions(self, mock_figure, mock_savefig):
        correct_predictions = [10, 20, 30]
        time_periods = [datetime(2024, 12, 5), datetime(2024, 12, 6), datetime(2024, 12, 7)]
        user_id = 1

        plot_cumulative_correct_predictions(correct_predictions, time_periods, user_id)

        mock_figure.assert_called_once_with(figsize=(8, 5))
        mock_savefig.assert_called_once_with(f'static/plots/model_cumulative_correct_predictions_{user_id}.png')

    @patch("Models.plotters.plt.savefig")
    @patch("Models.plotters.plt.figure")
    def test_plot_cumulative_incorrect_predictions(self, mock_figure, mock_savefig):
        incorrect_predictions = [5, 10, 15]
        time_periods = [datetime(2024, 12, 5), datetime(2024, 12, 6), datetime(2024, 12, 7)]
        user_id = 1

        plot_cumulative_incorrect_predictions(incorrect_predictions, time_periods, user_id)

        mock_figure.assert_called_once_with(figsize=(8, 5))
        mock_savefig.assert_called_once_with(f'static/plots/model_cumulative_incorrect_predictions_{user_id}.png')

    @patch("Models.plotters.plt.savefig")
    @patch("Models.plotters.plt.figure")
    def test_plot_time_to_close(self, mock_figure, mock_savefig):
        correct_close_times = [1, 2, 3, 4, 5]
        user_id = 1

        plot_time_to_close(correct_close_times, user_id)

        mock_figure.assert_called_once_with(figsize=(8, 5))
        mock_savefig.assert_called_once_with(f'static/plots/model_time_to_close_correct_{user_id}.png')

    @patch("Models.plotters.plt.savefig")
    @patch("Models.plotters.plt.figure")
    def test_plot_cumulative_profit(self, mock_figure, mock_savefig):
        profit_values = [100, 200, 300]
        time_periods = [datetime(2024, 12, 5), datetime(2024, 12, 6), datetime(2024, 12, 7)]
        user_id = 1

        plot_cumulative_profit(profit_values, time_periods, user_id)

        mock_figure.assert_called_once_with(figsize=(8, 5))
        mock_savefig.assert_called_once_with(f'static/plots/model_cumulative_profit_{user_id}.png')

    @patch("Models.plotters.plt.savefig")
    @patch("Models.plotters.plt.figure")
    def test_plot_cumulative_loss(self, mock_figure, mock_savefig):
        loss_values = [-100, -200, -300]
        time_periods = [datetime(2024, 12, 5), datetime(2024, 12, 6), datetime(2024, 12, 7)]
        user_id = 1

        plot_cumulative_loss(loss_values, time_periods, user_id)

        mock_figure.assert_called_once_with(figsize=(8, 5))
        mock_savefig.assert_called_once_with(f'static/plots/model_cumulative_loss_{user_id}.png')

    @patch("Models.plotters.plt.savefig")
    @patch("Models.plotters.plt.figure")
    def test_plot_model_sector_breakdown_profits(self, mock_figure, mock_savefig):
        sector_data = json.dumps({"Tech": 300, "Finance": 200})
        user_id = 1

        plot_model_sector_breakdown_profits(sector_data, user_id)

        mock_figure.assert_called_once_with(figsize=(8, 5))
        mock_savefig.assert_called_once_with(f'static/plots/model_sector_breakdown_profits_{user_id}.png')

    @patch("Models.plotters.plt.savefig")
    @patch("Models.plotters.plt.figure")
    def test_plot_model_sector_breakdown_loss(self, mock_figure, mock_savefig):
        sector_data = json.dumps({"Tech": -300, "Finance": -200})
        user_id = 1

        plot_model_sector_breakdown_loss(sector_data, user_id)

        mock_figure.assert_called_once_with(figsize=(8, 5))
        mock_savefig.assert_called_once_with(f'static/plots/model_sector_breakdown_loss_{user_id}.png')

    def test_generate_model_performance_graph(self):
        model_scores = {
            "dates": ["2024-12-05", "2024-12-06", "2024-12-07"],
            "accuracy": [85, 90, 95],
            "precision": [80, 85, 90],
            "recall": [75, 80, 85]
        }

        html_output = generate_model_performance_graph(model_scores)

        self.assertIn("<html>", html_output)
        self.assertIn("Model Performance Over Time", html_output)


if __name__ == "__main__":
    unittest.main()
