import unittest
from unittest.mock import patch, MagicMock
import pickle
from Models.model import Model 
from database import models_DAOIMPL 

class TestModel(unittest.TestCase):

    def setUp(self):
        """Set up mock models for testing."""
        self.mock_model = MagicMock()
        self.mock_model.get_accuracy.return_value = 0.95
        self.mock_model.get_precision.return_value = 0.93
        self.mock_model.get_recall.return_value = 0.92
        self.mock_model.get_f1_score.return_value = 0.94
        self.mock_model.get_top_features.return_value = ["feature1", "feature2", "feature3"]
        self.mock_model.get_last_trained.return_value = "2024-12-05"

        self.serialized_model = pickle.dumps(self.mock_model)

    @patch("models_DAOIMPL.get_comparison_trained_models")
    def test_get_selected_models(self, mock_get_comparison_trained_models):
        """Test that selected models are retrieved and deserialized correctly."""
        mock_get_comparison_trained_models.return_value = [
            MagicMock(model_name="Model A", model_data=self.serialized_model),
            MagicMock(model_name="Model B", model_data=self.serialized_model),
        ]

        selected_models = Model.get_selected_models()
        self.assertIsNotNone(selected_models)
        self.assertEqual(len(selected_models), 2)
        self.assertEqual(selected_models[0]['model_name'], "Model A")
        self.assertEqual(selected_models[1]['model_name'], "Model B")

    def test_get_model_metrics(self):
        """Test that metrics for models are calculated correctly."""
        models = [
            {'model_name': "Model A", 'model': self.mock_model},
            {'model_name': "Model B", 'model': self.mock_model},
        ]

        metrics = Model.get_model_metrics(models)
        self.assertEqual(len(metrics), 2)
        self.assertEqual(metrics[0]['model_name'], "Model A")
        self.assertEqual(metrics[0]['accuracy'], 0.95)
        self.assertEqual(metrics[0]['precision'], 0.93)
        self.assertEqual(metrics[0]['recall'], 0.92)
        self.assertEqual(metrics[0]['f1_score'], 0.94)
        self.assertEqual(metrics[0]['top_features'], ["feature1", "feature2", "feature3"])
        self.assertEqual(metrics[0]['last_trained'], "2024-12-05")

    @patch("models_DAOIMPL.get_model_blob_from_db_by_model_name_and_user_id")
    def test_retrieve_model_from_database(self, mock_get_model_blob):
        """Test retrieving a model from the database."""
        mock_get_model_blob.return_value = self.serialized_model

        model = Model.retrieve_model_from_database("Test Model", 1)
        self.assertIsNotNone(model)
        self.assertEqual(model.get_accuracy(), 0.95)

    @patch("models_DAOIMPL.get_model_blob_from_db_by_model_name_and_user_id")
    def test_retrieve_model_from_database_no_model(self, mock_get_model_blob):
        """Test behavior when no model is found in the database."""
        mock_get_model_blob.return_value = None

        with self.assertRaises(ValueError) as context:
            Model.retrieve_model_from_database("Test Model", 1)

        self.assertEqual(str(context.exception), "No model found for Test Model for user 1")

    def test_train_retrain_model(self):
        """Test training or retraining a model."""
        x_train = [[1, 2, 3], [4, 5, 6]]
        y_train = [0, 1]

        # Use a mock model with a `fit` method
        model = MagicMock()
        model.fit = MagicMock()

        trained_model = Model.train_retrain_model(model, x_train, y_train)
        model.fit.assert_called_once_with(x_train, y_train)
        self.assertEqual(trained_model, model)

    @patch("models_DAOIMPL.insert_model")
    def test_save_updated_model_back_to_db(self, mock_insert_model):
        """Test saving an updated model back to the database."""
        model = self.mock_model
        user_id = 1
        model_name = "Updated Model"
        model_description = "An updated model for testing."

        serialized_model = pickle.dumps(model)
        updated_model = Model(model_name, model_description, serialized_model, user_id, 1)

        Model.save_updated_model_back_to_db(model, model_name, model_description, user_id)
        mock_insert_model.assert_called_once_with(updated_model)


if __name__ == "__main__":
    unittest.main()
