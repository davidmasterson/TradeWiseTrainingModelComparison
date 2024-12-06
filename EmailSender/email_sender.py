
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

from datetime import datetime, date
from database import user_DAOIMPL





# Get environment variables from aws 


def send_email_of_closed_positions(opened, closed, user_id):
    email_sender_account = os.getenv('EMAIL_ADDRESS')
    smtp_port = os.getenv('SMTP_PORT')
    smtp_server = os.getenv('SMTP_SERVER')
    email_sender_user_name = os.getenv('EMAIL_SENDER_USER_NAME')
    email_password = os.getenv('EMAIL_PASSWORD')
    user = user_DAOIMPL.get_user_by_user_id(user_id)
    user_email = user[3]
    username = user[4]
    to_emails = [user_email]
    
    content = f'''
    Good evening {username},
    
    Please see the below listed positions that were purchased and closed during market hours on {date.today()}.
    Opened Positions
    {opened}
    
    Closed Positions
    {closed}
    
    Thank you for your continued support.
    
    Respectfully,
    David Masterson
    C.E.O and Founder Master Trade Tools, Inc.
    '''
    
    message = MIMEMultipart()
    message["From"] = email_sender_account
    message["To"] = to_emails
    message['Subject'] = f"Daily closed and purchased positions {date.today()}"
    message.attach(MIMEText(content, 'plain'))
    
    
    server = smtplib.SMTP(smtp_server,smtp_port)
    try:
        server.starttls()
    except Exception as e:
        print(f"{datetime.now()}:Unable to start ttls due to {e}")
    try:
        server.login(email_sender_user_name,email_password)
    except Exception as e:
        print(f"{datetime.now()}:unable to login to email server due to {e}")
    text = message.as_string()
    
    server.sendmail(email_sender_account,message['To'],text)
    server.quit()