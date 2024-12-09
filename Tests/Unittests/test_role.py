import unittest
from Models.role import Role  


class TestRole(unittest.TestCase):
    
    def test_initialization(self):
        """Test that Role initializes correctly."""
        role_name = "Admin"
        role = Role(role_name)
        
        # Assert that the role_name attribute is correctly set
        self.assertEqual(role.role_name, role_name)

    def test_attribute_type(self):
        """Test that role_name is a string."""
        role_name = "User"
        role = Role(role_name)
        
        # Assert that role_name is of type str
        self.assertIsInstance(role.role_name, str)


if __name__ == "__main__":
    unittest.main()
