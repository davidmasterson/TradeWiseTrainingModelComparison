import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from Models.password_resets import PasswordResets
import bcrypt
import database
from Models import password_resets


class TestPasswordResets(unittest.TestCase):

    @patch("password_resets.PasswordResets.secrets.token_urlsafe")
    @patch("password_resets.PasswordResets.bcrypt.hashpw")
    @patch("password_resets.PasswordResets.reset_password_DAOIMPL.insert_password_reset_token")
    def test_create_reset_token(self, mock_insert_token, mock_hashpw, mock_token_urlsafe):
        """Test creating a password reset token."""
        mock_token_urlsafe.return_value = "test_token"
        mock_hashpw.return_value = b"hashed_test_token"
        mock_insert_token.return_value = True
        password_reset = password_resets.PasswordResets(user_id=1, token=None, expiration_time=None, hashed_token=None)
        result = password_reset.create_reset_token(user_id=1)

        # Assertions
        mock_token_urlsafe.assert_called_once_with(32)
        mock_hashpw.assert_called_once_with("test_token".encode(), bcrypt.gensalt())
        mock_insert_token.assert_called_once()
        self.assertTrue(result)

    @patch("bcrypt.checkpw")
    @patch("database.reset_password_DAOIMPL.get_hashed_token_and_expiration_for_user")
    def test_validate_token_valid(self, mock_get_token_data, mock_checkpw):
        """Test validating a correct token."""
        mock_get_token_data.return_value = (b"hashed_test_token", datetime.now() + timedelta(minutes=15))
        mock_checkpw.return_value = True

        password_reset = password_resets.PasswordResets(user_id=1, token=None, expiration_time=None, hashed_token=None)
        result = password_reset.validate_token(user_id=1, provided_token="test_token")

        # Assertions
        mock_get_token_data.assert_called_once_with(1)
        mock_checkpw.assert_called_once_with("test_token".encode(), b"hashed_test_token")
        self.assertTrue(result)

    @patch("database.reset_password_DAOIMPL.get_hashed_token_and_expiration_for_user")
    def test_validate_token_expired(self, mock_get_token_data):
        """Test validating an expired token."""
        mock_get_token_data.return_value = (b"hashed_test_token", datetime.now() - timedelta(minutes=1))

        password_reset = password_resets.PasswordResets(user_id=1, token=None, expiration_time=None, hashed_token=None)
        result = password_reset.validate_token(user_id=1, provided_token="test_token")

        # Assertions
        mock_get_token_data.assert_called_once_with(1)
        self.assertFalse(result)

    @patch("bcrypt.checkpw")
    @patch("database.reset_password_DAOIMPL.get_hashed_token_and_expiration_for_user")
    def test_validate_token_invalid(self, mock_get_token_data, mock_checkpw):
        """Test validating an incorrect token."""
        mock_get_token_data.return_value = (b"hashed_test_token", datetime.now() + timedelta(minutes=15))
        mock_checkpw.return_value = False

        password_reset = password_resets.PasswordResets(user_id=1, token=None, expiration_time=None, hashed_token=None)
        result = password_reset.validate_token(user_id=1, provided_token="wrong_token")

        # Assertions
        mock_get_token_data.assert_called_once_with(1)
        mock_checkpw.assert_called_once_with("wrong_token".encode(), b"hashed_test_token")
        self.assertFalse(result)

    @patch("database.reset_password_DAOIMPL.delete_user_password_reset_token")
    def test_invalidate_password_reset_token(self, mock_delete_token):
        """Test invalidating a password reset token."""
        mock_delete_token.return_value = True

        password_reset = password_resets.PasswordResets(user_id=1, token=None, expiration_time=None, hashed_token=None)
        password_reset.invalidate_password_reset_token(user_id=1)

        # Assertions
        mock_delete_token.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()
