import unittest
import subprocess
from unittest.mock import patch, mock_open, MagicMock
import pickle
import tempfile
from Models.recommendation_script import RecommendationScript  


class TestRecommendationScript(unittest.TestCase):
    @patch("recommendation_scripts_DAOIMPL.get_recommendation_script_by_script_id")
    @patch("subprocess.run")
    @patch("builtins.open", new_callable=mock_open)
    @patch("pickle.loads")
    @patch("pickle.dumps")
    def test_retrainer_for_recommender(
        self, mock_dumps, mock_loads, mock_open, mock_subprocess, mock_get_script
    ):
        # Mock the DAO to return a list with a binary script
        mock_script = "print('Test Recommender Script')"
        mock_binary_script = pickle.dumps(mock_script)
        mock_get_script.return_value = [(1, "Test Script", "Description", mock_binary_script)]
        
        # Mock deserialization
        mock_loads.side_effect = [mock_script, {"result": "success"}]

        # Mock subprocess execution
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="Success", stderr="")

        # Call the method
        project_root = "/project/root"
        recommendation_script_id = 1
        user_id = 1
        dataset_id = 123

        result = RecommendationScript.retrainer_for_recommender(
            recommendation_script_id, project_root, user_id, dataset_id
        )

        # Assertions
        mock_get_script.assert_called_once_with(recommendation_script_id)
        mock_subprocess.assert_called_once()
        mock_open.assert_called()  # Verify temporary files are opened
        mock_loads.assert_called()  # Ensure deserialization is performed
        self.assertEqual(result["result"], "success")

    @patch("recommendation_scripts_DAOIMPL.get_recommendation_script_by_script_id")
    def test_retrainer_for_recommender_no_script(self, mock_get_script):
        # Mock the DAO to return an empty list (no script found)
        mock_get_script.return_value = []

        project_root = "/project/root"
        recommendation_script_id = 1
        user_id = 1
        dataset_id = 123

        with self.assertRaises(IndexError):
            RecommendationScript.retrainer_for_recommender(
                recommendation_script_id, project_root, user_id, dataset_id
            )

    @patch("recommendation_scripts_DAOIMPL.get_recommendation_script_by_script_id")
    @patch("subprocess.run")
    @patch("pickle.loads")
    def test_retrainer_for_recommender_subprocess_error(
        self, mock_loads, mock_subprocess, mock_get_script
    ):
        # Mock the DAO to return a valid script
        mock_script = "print('Test Recommender Script')"
        mock_binary_script = pickle.dumps(mock_script)
        mock_get_script.return_value = [(1, "Test Script", "Description", mock_binary_script)]
        
        # Mock subprocess execution to simulate an error
        mock_subprocess.return_value = MagicMock(returncode=1, stdout="", stderr="Error in script execution")

        project_root = "/project/root"
        recommendation_script_id = 1
        user_id = 1
        dataset_id = 123

        with self.assertRaises(RuntimeError):
            RecommendationScript.retrainer_for_recommender(
                recommendation_script_id, project_root, user_id, dataset_id
            )


if __name__ == "__main__":
    unittest.main()
