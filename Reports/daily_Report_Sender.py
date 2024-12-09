import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Models import Reports
from database import user_DAOIMPL
import logging

all_users = user_DAOIMPL.get_all_users()
logging.info(f'All users in db are {all_users}')
logging.info('Iterating through uers list to create a reports object')
for user in all_users:
    try:
        logging.info(f'Creating a reports object for {user["user_name"]}')
        report = Reports.Report(user, user["id"])
        logging.info(f'Reports object successfully created for {user["user_name"]}')
        logging.info(f'Sending end of day report for {user["user_name"]} to email address {user["email"]}')
        Reports.Report.create_and_send_end_of_day_report(report)
        logging.info(f'Successfully sent end of day report to {user["user_name"]} sending next report')
    except Exception as e:
        logging.error(f'Was unable to send end of day report to {user["user_name"]} due to {e}')
        continue