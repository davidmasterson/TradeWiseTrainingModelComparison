import unittest
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime, date
from database import user_DAOIMPL
import base64
from EmailSender.email_sender import send_email_of_closed_positions  


class TestSendEmailOfClosedPositions(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data=b"fake_image_data")
    @patch("os.getenv")
    @patch("user_DAOIMPL.get_user_by_user_id")  
    @patch("EmailSender.email_sender.smtplib.SMTP")
    def test_send_email_successful(
        self, mock_smtp, mock_get_user, mock_getenv, mock_file
    ):
        # Mock data
        mock_getenv.side_effect = lambda key: {
            "EMAIL_ADDRESS": "test@example.com",
            "SMTP_PORT": "587",
            "SMTP_SERVER": "smtp.example.com",
            "EMAIL_SENDER_USER_NAME": "sender_user",
            "EMAIL_PASSWORD": "password",
        }.get(key)

        mock_get_user.return_value = [1, "user1", "user2", "user@example.com", "Test User"]

        mock_smtp_instance = mock_smtp.return_value
        mock_smtp_instance.sendmail = MagicMock()
        mock_smtp_instance.quit = MagicMock()

        opens = [
            {"symbol": "AAPL", "qty": 10, "purchase_price": 150, "total_purchase": 1500}
        ]
        closes = [
            {
                "symbol": "GOOG",
                "qty": 5,
                "purchase_price": 1000,
                "total_purchase": 5000,
                "sell_price": 1200,
                "total_sell": 6000,
                "actual_return": 1000,
                "percentroi": 20,
            }
        ]

        # Call function
        send_email_of_closed_positions(opens, closes, 1)

        # Assert environment variables are fetched
        mock_getenv.assert_any_call("EMAIL_ADDRESS")
        mock_getenv.assert_any_call("SMTP_PORT")
        mock_getenv.assert_any_call("SMTP_SERVER")
        mock_getenv.assert_any_call("EMAIL_SENDER_USER_NAME")
        mock_getenv.assert_any_call("EMAIL_PASSWORD")

        # Assert user DAO is called
        mock_get_user.assert_called_once_with(1)

        # Assert the email was sent
        mock_smtp_instance.sendmail.assert_called_once()
        mock_smtp_instance.quit.assert_called_once()

    @patch("builtins.open", side_effect=FileNotFoundError)
    @patch("os.getenv")
    @patch("your_module.user_DAOIMPL.get_user_by_user_id")
    def test_send_email_image_not_found(self, mock_get_user, mock_getenv, mock_file):
        # Mock data
        mock_getenv.side_effect = lambda key: {
            "EMAIL_ADDRESS": "test@example.com",
            "SMTP_PORT": "587",
            "SMTP_SERVER": "smtp.example.com",
            "EMAIL_SENDER_USER_NAME": "sender_user",
            "EMAIL_PASSWORD": "password",
        }.get(key)

        mock_get_user.return_value = [1, "user1", "user2", "user@example.com", "Test User"]

        opens = []
        closes = []

        # Call function and expect no exception raised
        with self.assertRaises(FileNotFoundError):
            send_email_of_closed_positions(opens, closes, 1)

    @patch("EmailSender.email_sender.smtplib.SMTP")
    def test_smtp_exceptions(self, mock_smtp):
        mock_smtp_instance = mock_smtp.return_value
        mock_smtp_instance.starttls.side_effect = Exception("StartTLS failed")
        mock_smtp_instance.login.side_effect = Exception("Login failed")

        with self.assertLogs(level='DEBUG') as log:
            send_email_of_closed_positions([], [], 1)
            self.assertIn("Unable to start ttls due to StartTLS failed", log.output[-2])
            self.assertIn("unable to login to email server due to Login failed", log.output[-1])


if __name__ == "__main__":
    unittest.main()
