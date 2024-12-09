import unittest
from unittest.mock import patch, MagicMock
from Models.progress_object import Progress 
from database import progression_DAOIMPL 


class TestProgress(unittest.TestCase):

    def setUp(self):
        """Set up mock data for Progress tests."""
        self.progress = 75  
        self.user_id = 1
        self.progress_instance = Progress(self.progress, self.user_id)

    def test_initialization(self):
        """Test that Progress initializes correctly."""
        self.assertEqual(self.progress_instance.progress, self.progress)
        self.assertEqual(self.progress_instance.user_id, self.user_id)

    def test_attributes_type(self):
        """Test that attributes are of the correct type."""
        self.assertIsInstance(self.progress_instance.progress, int)
        self.assertIsInstance(self.progress_instance.user_id, int)

    @patch("database.progression_DAOIMPL.update_user_progress")
    def test_update_user_progress(self, mock_update_progress):
        """Test updating user progress in the database."""
        mock_update_progress.return_value = True

        result = progression_DAOIMPL.update_user_progress(self.user_id, self.progress)

        # Assert that the DAO method was called with the correct parameters
        mock_update_progress.assert_called_once_with(self.user_id, self.progress)
        self.assertTrue(result)

    @patch("database.progression_DAOIMPL.get_user_progress")
    def test_get_user_progress(self, mock_get_progress):
        """Test retrieving user progress from the database."""
        mock_get_progress.return_value = self.progress

        retrieved_progress = progression_DAOIMPL.get_user_progress(self.user_id)

        # Assert that the DAO method was called with the correct user_id
        mock_get_progress.assert_called_once_with(self.user_id)
        self.assertEqual(retrieved_progress, self.progress)


if __name__ == "__main__":
    unittest.main()
