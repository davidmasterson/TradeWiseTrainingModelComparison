import unittest
from unittest.mock import patch, MagicMock, mock_open
import pickle
import tempfile
from Models.preprocessing_script import Preprocessing_Script 
from database import preprocessing_scripts_DAOIMPL 


class TestPreprocessingScript(unittest.TestCase):
    @patch("database.preprocessing_scripts_DAOIMPL.update_preprocessed_data_for_user")
    @patch("database.preprocessing_scripts_DAOIMPL.insert_preprocessing_script_for_user")
    @patch("builtins.exec")
    def test_execute_preprocessing_and_save(
        self, mock_exec, mock_insert_script, mock_update_script
    ):
        script_content = """
X_train = [1, 2, 3]
y_train = [0, 1, 0]
X_test = [4, 5]
y_test = [1, 0]
"""
        model_name = "TestModel"
        user_id = 1
        existing_preprocessed_data = None

        Preprocessing_Script.execute_preprocessing_and_save(
            script_content, existing_preprocessed_data, model_name, user_id
        )

        mock_exec.assert_called_once_with(script_content, globals(), {})
        mock_insert_script.assert_called_once()

    @patch("database.preprocessing_scripts_DAOIMPL.get_preprocessed_script_by_id")
    @patch("subprocess.run")
    @patch("database.dataset_DAOIMPL.update_dataset")
    @patch("database.dataset_DAOIMPL.get_dataset_object_by_id")
    @patch("builtins.open", new_callable=mock_open)
    @patch("pickle.load")
    @patch("pickle.dumps")
    def test_retrainer_preprocessor(
        self,
        mock_dumps,
        mock_load,
        mock_open,
        mock_get_dataset,
        mock_update_dataset,
        mock_subprocess,
        mock_get_script,
    ):
        mock_script = "print('Test Script')"
        mock_binary_script = pickle.dumps(mock_script)
        mock_preprocessed_data = {
            "preprocessing_object": MagicMock(),
            "dataset": MagicMock(),
        }
        mock_dataset_object = MagicMock()

        mock_get_script.return_value = mock_binary_script
        mock_load.side_effect = [mock_preprocessed_data, mock_dataset_object]
        mock_get_dataset.return_value = ("name", "description", "data")
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="Success")

        Preprocessing_Script.retrainer_preprocessor(
            preprocessing_script_id=1,
            project_root="/project/root",
            dataset_id=1,
            user_id=1,
            model_name="TestModel",
        )

        mock_subprocess.assert_called_once()
        mock_update_dataset.assert_called_once()

    @patch("database.preprocessing_scripts_DAOIMPL.get_preprocessed_script_by_id")
    @patch("subprocess.run")
    @patch("builtins.open", new_callable=mock_open)
    @patch("pickle.load")
    def test_retrainer_preprocessor_for_recommender(
        self, mock_load, mock_open, mock_subprocess, mock_get_script
    ):
        mock_script = "print('Test Script')"
        mock_binary_script = pickle.dumps(mock_script)
        mock_get_script.return_value = mock_binary_script
        mock_load.return_value = {"result": "Test"}

        mock_subprocess.return_value = MagicMock(returncode=0, stdout="Success")

        result = Preprocessing_Script.retrainer_preprocessor_for_recommender(
            preprocessing_script_id=1,
            project_root="/project/root",
            dataset_id=1,
            user_id=1,
            model_name="TestModel",
        )

        mock_subprocess.assert_called_once()
        self.assertEqual(result.returncode, 0)

    def test_execute_preprocessing_and_save_no_script(self):
        with self.assertRaises(ValueError) as context:
            Preprocessing_Script.execute_preprocessing_and_save(
                None, None, "TestModel", 1
            )
        self.assertEqual(
            str(context.exception), "No preprocessing script found for model: TestModel"
        )


if __name__ == "__main__":
    unittest.main()
