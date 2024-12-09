import unittest
from unittest.mock import patch, MagicMock
from Reports.daily_Report_Sender import  all_users
from Models import Reports
import logging
from database import user_DAOIMPL


class TestEndOfDayReports(unittest.TestCase):

    @patch("user_DAOIMPL.get_all_users")
    @patch("Reports.Report")
    def test_successful_end_of_day_reports(self, mock_report, mock_get_all_users):
        """Test successful creation and sending of end-of-day reports for all users."""
        # Mock user list
        mock_get_all_users.return_value = [
            {"user_name": "user1", "id": 1, "email": "user1@example.com"},
            {"user_name": "user2", "id": 2, "email": "user2@example.com"}
        ]

        # Mock report object behavior
        mock_report_instance = MagicMock()
        mock_report.return_value = mock_report_instance

        # Run the script logic
        for user in mock_get_all_users.return_value:
            try:
                report = Reports.Report(user, user["id"])
                Reports.Report.create_and_send_end_of_day_report(report)
            except Exception as e:
                logging.error(f"Error processing user {user['user_name']}: {e}")

        # Assert that reports were created and sent for all users
        self.assertEqual(mock_report.call_count, 2)
        self.assertEqual(mock_report_instance.create_and_send_end_of_day_report.call_count, 2)

        # Verify specific calls
        mock_report.assert_any_call({"user_name": "user1", "id": 1, "email": "user1@example.com"}, 1)
        mock_report.assert_any_call({"user_name": "user2", "id": 2, "email": "user2@example.com"}, 2)

    @patch("user_DAOIMPL.get_all_users")
    @patch("Reports.Report.create_and_send_end_of_day_report")
    @patch("Reports.Report")
    def test_error_handling_in_report_generation(self, mock_report, mock_send_report, mock_get_all_users):
        """Test error handling during report generation and email sending."""
        # Mock user list with one valid and one problematic user
        mock_get_all_users.return_value = [
            {"user_name": "user1", "id": 1, "email": "user1@example.com"},
            {"user_name": "user2", "id": 2, "email": "user2@example.com"}
        ]

        # Mock report creation
        mock_report.side_effect = [MagicMock(), Exception("Report creation failed")]

        # Run the script logic
        for user in mock_get_all_users.return_value:
            try:
                report = Reports.Report(user, user["id"])
                Reports.Report.create_and_send_end_of_day_report(report)
            except Exception as e:
                logging.error(f"Error processing user {user['user_name']}: {e}")

        # Assert first report was created and email sent
        self.assertEqual(mock_report.call_count, 2)
        mock_send_report.assert_called_once()  # Only one successful report sending

        # Assert logging for error handling
        self.assertLogs("Error processing user user2: Report creation failed")

    @patch("user_DAOIMPL.get_all_users")
    def test_no_users_in_database(self, mock_get_all_users):
        """Test script behavior when no users are found in the database."""
        mock_get_all_users.return_value = []  # Simulate empty user list

        # Run the script logic
        for user in mock_get_all_users.return_value:
            try:
                report = Reports.Report(user, user["id"])
                Reports.Report.create_and_send_end_of_day_report(report)
            except Exception as e:
                logging.error(f"Error processing user {user['user_name']}: {e}")

        # Assert no reports created or emails sent
        self.assertEqual(len(mock_get_all_users.return_value), 0)


if __name__ == "__main__":
    unittest.main()
