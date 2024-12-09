import unittest
from database import transactions_DAOIMPL
from unittest.mock import patch, MagicMock
from datetime import date, datetime
from Models.Reports import Report  
from EmailSender import email_sender
import logging


class TestReport(unittest.TestCase):
    
    @patch("EmailSender.email_sender.send_email_of_closed_positions")
    @patch("transactions_DAOIMPL.get_transactions_for_user_by_sell_date")
    @patch("transactions_DAOIMPL.get_transactions_for_user_by_purchase_date")
    @patch("logging.info")
    @patch("logging.error")
    def test_create_and_send_end_of_day_report_success(
        self, mock_logging_error, mock_logging_info, mock_get_opened, mock_get_closed, mock_send_email
    ):
        """Test successful end-of-day report creation and sending."""
        # Mock user and transactions
        user = {"user_name": "test_user"}
        user_id = 1
        mock_get_opened.return_value = [
            (1, "AAPL", date.today(), 150.0, 10),
        ]
        mock_get_closed.return_value = [
            (1, "MSFT", date.today(), 300.0, 5, None, None, None, 310.0, 1550.0, None, None, 5.0, 50.0),
        ]

        # Initialize the Report object
        report = Report(user_object=user, user_id=user_id)

        # Call the method
        report.create_and_send_end_of_day_report()

        # Assert that transactions were retrieved
        mock_get_opened.assert_called_once_with(user_id, date.today())
        mock_get_closed.assert_called_once_with(user_id, date.today())

        # Assert that email was sent
        mock_send_email.assert_called_once()

        # Assert logging
        mock_logging_info.assert_called_with(f'{datetime.now()}: Started end of day clean up for user test_user')

    @patch("EmailSender.email_sender.send_email_of_closed_positions")
    @patch("transactions_DAOIMPL.transactions_DAOIMPL.get_transactions_for_user_by_sell_date")
    @patch("transactions_DAOIMPL.transactions_DAOIMPL.get_transactions_for_user_by_purchase_date")
    @patch("logging.error")
    def test_create_and_send_end_of_day_report_failure(
        self, mock_logging_error, mock_get_opened, mock_get_closed, mock_send_email
    ):
        """Test failure during end-of-day report creation."""
        # Mock user and transactions
        user = {"user_name": "test_user"}
        user_id = 1
        mock_get_opened.side_effect = Exception("Database error")

        # Initialize the Report object
        report = Report(user_object=user, user_id=user_id)

        # Call the method
        report.create_and_send_end_of_day_report()

        # Assert logging error
        mock_logging_error.assert_called_once()
        mock_send_email.assert_not_called()  # Ensure email is not sent


if __name__ == "__main__":
    unittest.main()
