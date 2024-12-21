import unittest
from unittest.mock import patch
from Models import user 
import bcrypt
from database import roles_DAOIMPL


class TestUser(unittest.TestCase):

    @patch("flask.session")
    def test_check_logged_in_true(self, mock_session):
        """Test that check_logged_in returns True when user is logged in."""
        mock_session.get.return_value = True

        result = user.User.check_logged_in()

        self.assertTrue(result)
        mock_session.get.assert_called_once_with('logged_in')

    @patch("flask.session")
    def test_check_logged_in_false(self, mock_session):
        """Test that check_logged_in returns False when user is not logged in."""
        mock_session.get.return_value = False

        result = user.User.check_logged_in()

        self.assertFalse(result)
        mock_session.get.assert_called_once_with('logged_in')

    def test_hash_password(self):
        """Test that hash_password hashes the password correctly."""
        password = "securepassword123"
        hashed_password = user.User.hash_password(password)

        self.assertIsInstance(hashed_password, bytes)
        self.assertTrue(bcrypt.checkpw(password.encode('utf-8'), hashed_password))

    @patch("flask.session")
    @patch("database.roles_DAOIMPL.get_user_role_by_user_id")
    @patch("Models.user.User.check_logged_in")
    def test_get_current_user_role(self, mock_check_logged_in, mock_get_user_role, mock_session):
        """Test that get_current_user_role returns the correct role for a logged-in user."""
        mock_check_logged_in.return_value = True
        mock_session.get.return_value = 1
        mock_get_user_role.return_value = "admin"

        result = user.User.get_current_user_role()

        self.assertEqual(result, "admin")
        mock_check_logged_in.assert_called_once()
        mock_session.get.assert_called_once_with('user_id')
        mock_get_user_role.assert_called_once_with(1)

    @patch("flask.session")
    @patch("Models.user.User.check_logged_in")
    def test_get_id(self, mock_check_logged_in, mock_session):
        """Test that get_id returns the user ID when logged in."""
        mock_check_logged_in.return_value = True
        mock_session.get.return_value = 1

        result = user.User.get_id()

        self.assertEqual(result, 1)
        mock_check_logged_in.assert_called_once()
        mock_session.get.assert_called_once_with('user_id')

    @patch("flask.session")
    @patch("Models.user.User.check_logged_in")
    def test_get_id_not_logged_in(self, mock_check_logged_in, mock_session):
        """Test that get_id returns None when user is not logged in."""
        mock_check_logged_in.return_value = False

        result = user.User.get_id()

        self.assertIsNone(result)
        mock_check_logged_in.assert_called_once()
        mock_session.get.assert_not_called()


if __name__ == "__main__":
    unittest.main()
