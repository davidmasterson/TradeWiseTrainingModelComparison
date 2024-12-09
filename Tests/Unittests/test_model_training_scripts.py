import unittest
from Models.models_training_scripts import ModelsTrainingScripts  # Replace `your_module` with the actual module name


class TestModelsTrainingScripts(unittest.TestCase):
    
    def setUp(self):
        """Set up test data for ModelsTrainingScripts."""
        self.model_id = 1
        self.training_script_id = 101
        self.models_training_script = ModelsTrainingScripts(
            model_id=self.model_id,
            training_script_id=self.training_script_id
        )

    def test_initialization(self):
        """Test that ModelsTrainingScripts initializes correctly."""
        self.assertEqual(self.models_training_script.model_id, self.model_id)
        self.assertEqual(self.models_training_script.training_script_id, self.training_script_id)

    def test_attributes_type(self):
        """Test that attributes have the correct types."""
        self.assertIsInstance(self.models_training_script.model_id, int)
        self.assertIsInstance(self.models_training_script.training_script_id, int)


if __name__ == "__main__":
    unittest.main()
