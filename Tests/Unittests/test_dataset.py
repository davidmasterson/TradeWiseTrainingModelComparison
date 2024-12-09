

import unittest
from datetime import datetime
from Models import dataset

# Assuming Dataset class is defined in dataset.py
# from dataset import Dataset

class TestDataset(unittest.TestCase):
    def setUp(self):
        """Set up test data for the Dataset class."""
        self.dataset_name = "Test Dataset"
        self.dataset_description = "This is a test dataset."
        self.dataset_data = b"Test binary data"
        self.uploaded_at = datetime.now()
        self.user_id = 123

        self.dataset = dataset.Dataset(
            dataset_name=self.dataset_name,
            dataset_description=self.dataset_description,
            dataset_data=self.dataset_data,
            uploaded_at=self.uploaded_at,
            user_id=self.user_id,
        )

    def test_initialization(self):
        """Test that the Dataset class initializes with correct attributes."""
        self.assertEqual(self.dataset.dataset_name, self.dataset_name)
        self.assertEqual(self.dataset.dataset_description, self.dataset_description)
        self.assertEqual(self.dataset.dataset_data, self.dataset_data)
        self.assertEqual(self.dataset.uploaded_at, self.uploaded_at)
        self.assertEqual(self.dataset.user_id, self.user_id)

    def test_dataset_name_type(self):
        """Test that dataset_name is of type str."""
        self.assertIsInstance(self.dataset.dataset_name, str)

    def test_dataset_description_type(self):
        """Test that dataset_description is of type str."""
        self.assertIsInstance(self.dataset.dataset_description, str)

    def test_dataset_data_type(self):
        """Test that dataset_data is of type bytes."""
        self.assertIsInstance(self.dataset.dataset_data, bytes)

    def test_uploaded_at_type(self):
        """Test that uploaded_at is of type datetime."""
        self.assertIsInstance(self.dataset.uploaded_at, datetime)

    def test_user_id_type(self):
        """Test that user_id is of type int."""
        self.assertIsInstance(self.dataset.user_id, int)


if __name__ == "__main__":
    unittest.main()
