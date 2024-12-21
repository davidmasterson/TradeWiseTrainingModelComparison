import unittest
from unittest.mock import patch, MagicMock
from Models.user_role import UserRole 
from Models import user 
from flask import session
from database import roles_DAOIMPL
import flask

class TestUserRole(unittest.TestCase):

    @patch("flask.session")
    @patch("database.roles_DAOIMPL.get_user_role_by_user_id")
    def test_check_if_admin_is_admin(self, mock_get_user_role, mock_session):
        """Test that check_if_admin returns True for an admin user."""
        mock_session.get.return_value = 1  # Mock user ID in session
        mock_get_user_role.return_value = 'admin'  # Mock admin role

        result = UserRole.check_if_admin(self)

        # Assert that the method returns True for an admin
        self.assertTrue(result)

        # Assert that the session and DAO methods were called
        mock_session.get.assert_called_once_with('user_id')
        mock_get_user_role.assert_called_once_with(1)

    @patch("flask.session")
    @patch("database.roles_DAOIMPL.get_user_role_by_user_id")
    def test_check_if_admin_is_not_admin(self, mock_get_user_role, mock_session):
        """Test that check_if_admin returns False for a non-admin user."""
        mock_session.get.return_value = 2  # Mock user ID in session
        mock_get_user_role.return_value = 'user'  # Mock non-admin role

        result = UserRole.check_if_admin(self)

        # Assert that the method returns False for a non-admin
        self.assertFalse(result)

        # Assert that the session and DAO methods were called
        mock_session.get.assert_called_once_with('user_id')
        mock_get_user_role.assert_called_once_with(2)

    @patch("flask.session")
    @patch("database.roles_DAOIMPL.get_user_role_by_user_id")
    def test_check_if_admin_no_user_in_session(self, mock_get_user_role, mock_session):
        """Test that check_if_admin returns False if no user ID is in the session."""
        mock_session.get.return_value = None  # No user ID in session

        result = UserRole.check_if_admin(self)

        # Assert that the method returns False
        self.assertFalse(result)

        # Assert that the DAO method was not called
        mock_session.get.assert_called_once_with('user_id')
        mock_get_user_role.assert_not_called()


if __name__ == "__main__":
    unittest.main()
