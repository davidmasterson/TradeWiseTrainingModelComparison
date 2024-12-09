import unittest
import subprocess
from unittest.mock import patch, mock_open, MagicMock
from database import training_scripts_DAOIMPL, models_DAOIMPL, model_metrics_history_DAOIMPL
from Models.training_script import TrainingScript  
import json
import pickle
from datetime import datetime


class TestTrainingScript(unittest.TestCase):

    @patch("training_scripts_DAOIMPL.get_training_script_data_by_id")
    @patch("subprocess.run")
    @patch("models_DAOIMPL.get_model_from_db_by_model_name_and_user_id")
    @patch("models_DAOIMPL.update_model_for_user")
    @patch("models_DAOIMPL.insert_model_into_models_for_user")
    @patch("model_metrics_history_DAOIMPL.insert_metrics_history")
    @patch("sklearn.metrics.accuracy_score")
    @patch("sklearn.metricsprecision_score")
    @patch("sklearn.metricsrecall_score")
    @patch("sklearn.metricsf1_score")
    def test_model_trainer_success(
        self,
        mock_f1_score,
        mock_recall_score,
        mock_precision_score,
        mock_accuracy_score,
        mock_insert_metrics_history,
        mock_insert_model,
        mock_update_model,
        mock_get_model,
        mock_subprocess,
        mock_get_training_script
    ):
        """Test successful execution of model_trainer."""
        # Mock inputs and dependencies
        training_script = "print('Training script')"
        mock_get_training_script.return_value = training_script

        # Mock subprocess output
        mock_model_binary = pickle.dumps(MagicMock(feature_importances_=[0.5, 0.3, 0.2]))
        subprocess_output = json.dumps({
            "model_binary": mock_model_binary.hex(),
            "y_pred": [1, 0, 1],
            "y_test": [1, 0, 0],
            "columns": ["Feature1", "Feature2", "Feature3"]
        })
        mock_subprocess.return_value = MagicMock(returncode=0, stdout=subprocess_output)

        # Mock database interactions
        mock_get_model.return_value = None  # Simulate no existing model
        mock_insert_model.return_value = 1  # Simulate model ID

        # Mock metrics
        mock_accuracy_score.return_value = 0.9
        mock_precision_score.return_value = 0.85
        mock_recall_score.return_value = 0.8
        mock_f1_score.return_value = 0.82

        # Call the method
        TrainingScript.model_trainer(
            training_script_id=1,
            preprocessing_script_id=2,
            model_id=3,
            user_id=1,
            model_name="TestModel",
            project_root="/project/root"
        )

        # Assertions
        mock_get_training_script.assert_called_once_with(1)
        mock_subprocess.assert_called_once()
        mock_insert_model.assert_called_once()
        mock_accuracy_score.assert_called_once()
        mock_precision_score.assert_called_once()
        mock_recall_score.assert_called_once()
        mock_f1_score.assert_called_once()
        mock_insert_metrics_history.assert_called_once()

    @patch("subprocess.run")
    def test_model_trainer_failure(self, mock_subprocess):
        """Test model_trainer failure due to subprocess error."""
        # Mock subprocess error
        mock_subprocess.return_value = MagicMock(returncode=1, stderr="Error in script execution")

        with self.assertRaises(RuntimeError):
            TrainingScript.model_trainer(
                training_script_id=1,
                preprocessing_script_id=2,
                model_id=3,
                user_id=1,
                model_name="TestModel",
                project_root="/project/root"
            )

    @patch("training_scripts_DAOIMPL.get_training_script_data_by_id")
    @patch("subprocess.run")
    def test_model_trainer_deserialization_error(self, mock_subprocess, mock_get_training_script):
        """Test deserialization error in model_trainer."""
        training_script = "print('Training script')"
        mock_get_training_script.return_value = training_script

        # Mock subprocess output with invalid binary data
        subprocess_output = json.dumps({
            "model_binary": "invalid_hex",
            "y_pred": [1, 0, 1],
            "y_test": [1, 0, 0],
            "columns": ["Feature1", "Feature2", "Feature3"]
        })
        mock_subprocess.return_value = MagicMock(returncode=0, stdout=subprocess_output)

        with self.assertRaises(ValueError):
            TrainingScript.model_trainer(
                training_script_id=1,
                preprocessing_script_id=2,
                model_id=3,
                user_id=1,
                model_name="TestModel",
                project_root="/project/root"
            )


if __name__ == "__main__":
    unittest.main()
