import unittest
from datetime import datetime
from Models.model_metrics_history import Model_Metrics_History  


class TestModelMetricsHistory(unittest.TestCase):
    
    def setUp(self):
        """Set up test data for Model_Metrics_History."""
        self.metric_1 = Model_Metrics_History(
            model_id=1,
            accuracy=0.95,
            precision=0.92,
            recall=0.93,
            f1_score=0.915,
            top_features='["feature1", "feature2", "feature3"]',
            timestamp=datetime(2024, 12, 5, 12, 0, 0)
        )
        self.metric_2 = Model_Metrics_History(
            model_id=2,
            accuracy=0.90,
            precision=0.88,
            recall=0.89,
            f1_score=0.885,
            top_features='["feature4", "feature5", "feature6"]',
            timestamp=datetime(2024, 12, 6, 14, 30, 0)
        )
        self.metric_3 = Model_Metrics_History(
            model_id=3,
            accuracy=0.85,
            precision=0.80,
            recall=0.82,
            f1_score=0.81,
            top_features='["feature7", "feature8", "feature9"]',
            timestamp=datetime(2024, 12, 4, 9, 15, 0)
        )

    def test_initialization(self):
        """Test that Model_Metrics_History initializes correctly."""
        self.assertEqual(self.metric_1.model_id, 1)
        self.assertEqual(self.metric_1.accuracy, 0.95)
        self.assertEqual(self.metric_1.precision, 0.92)
        self.assertEqual(self.metric_1.recall, 0.93)
        self.assertEqual(self.metric_1.f1_score, 0.915)
        self.assertEqual(self.metric_1.top_features, '["feature1", "feature2", "feature3"]')
        self.assertEqual(self.metric_1.timestamp, datetime(2024, 12, 5, 12, 0, 0))

    def test_get_most_recent_metric(self):
        """Test the get_most_recent_metric method."""
        metrics = [
            [1, 2, 0.95, 0.92, 0.93, 0.915, '["feature1", "feature2", "feature3"]', datetime(2024, 12, 5, 12, 0, 0)],
            [2, 5, 0.90, 0.88, 0.89, 0.885, '["feature4", "feature5", "feature6"]', datetime(2024, 12, 6, 14, 30, 0)],
            [3, 6, 0.85, 0.80, 0.82, 0.81, '["feature7", "feature8", "feature9"]', datetime(2024, 12, 4, 9, 15, 0)],
        ]

        most_recent = Model_Metrics_History.get_most_recent_metric(metrics)

        # Check that the most recent metric is returned
        self.assertEqual(most_recent[0], 2)  # model_id of the most recent metric
        self.assertEqual(most_recent[2], 0.90)  # accuracy of the most recent metric
        self.assertEqual(most_recent[7], datetime(2024, 12, 6, 14, 30, 0))  # timestamp of the most recent metric

    def test_get_most_recent_metric_empty(self):
        """Test get_most_recent_metric with an empty list."""
        metrics = []
        most_recent = Model_Metrics_History.get_most_recent_metric(metrics)
        self.assertIsNone(most_recent)

    def test_get_most_recent_metric_single_entry(self):
        """Test get_most_recent_metric with a single entry."""
        metrics = [
            [1, 6, 0.95, 0.92, 0.93, 0.915, '["feature1", "feature2", "feature3"]', datetime(2024, 12, 5, 12, 0, 0)],
        ]
        most_recent = Model_Metrics_History.get_most_recent_metric(metrics)
        self.assertEqual(most_recent[0], 1)  # model_id of the only metric
        self.assertEqual(most_recent[7], datetime(2024, 12, 5, 12, 0, 0))  # timestamp of the only metric


if __name__ == "__main__":
    unittest.main()
