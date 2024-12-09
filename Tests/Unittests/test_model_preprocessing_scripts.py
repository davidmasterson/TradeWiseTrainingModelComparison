
import unittest
from Models.models_preprocessing_scripts import ModelPreProcessingScripts  


class TestModelPreProcessingScripts(unittest.TestCase):
    
    def setUp(self):
        """Set up test data for ModelPreProcessingScripts."""
        self.model_id = 1
        self.preprocessing_script_id = 42
        self.model_preprocessing_script = ModelPreProcessingScripts(
            model_id=self.model_id,
            preprocessing_script_id=self.preprocessing_script_id
        )

    def test_initialization(self):
        """Test that ModelPreProcessingScripts initializes correctly."""
        self.assertEqual(self.model_preprocessing_script.model_id, self.model_id)
        self.assertEqual(self.model_preprocessing_script.preprocessing_script_id, self.preprocessing_script_id)

    def test_attributes_type(self):
        """Test that attributes have the correct types."""
        self.assertIsInstance(self.model_preprocessing_script.model_id, int)
        self.assertIsInstance(self.model_preprocessing_script.preprocessing_script_id, int)


if __name__ == "__main__":
    unittest.main()
