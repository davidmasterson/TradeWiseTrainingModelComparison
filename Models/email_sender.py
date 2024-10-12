import smtplib
import base64
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import OAuth2_0
import logging
from datetime import datetime
import time

class EmailSender:
    
    def __init__(self, to_emails):
        self.to_emails = to_emails
        self.email_username = os.getenv('EMAIL_SENDER_USER_NAME')
        self.smtp_port = int(os.getenv('SMTP_PORT'))
        self.smtp_server = os.getenv('SMTP_SERVER')
        self.from_email = os.getenv('EMAIL_ADDRESS')
        self.from_email_password = os.getenv('EMAIL_PASSWORD')
        
        
    def send_reset_email(self, token):
        self.to_emails = self.to_emails[0]
        
        # Create the message
        message = MIMEMultipart()
        message["From"] = self.from_email
        message["To"] = [self.to_emails][0]
        message['Subject'] = 'Password Reset Request'
        reset_link = f"http://localhost:5000/reset_password/{token}"
        body = f"""
        Hello,

        You requested to reset your password. Please use the following link to reset it:
        {reset_link}

        This link will expire in 15 minutes. If you didn't request this, please ignore the email.

        Thank you!
        """
        message.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(self.smtp_server,self.smtp_port)
        try:
            server.starttls()
        except Exception as e:
            print(f"{datetime.now()}:Unable to start ttls due to {e}")
        try:
            server.login(self.email_username,self.from_email_password)
        except Exception as e:
            print(f"{datetime.now()}:unable to login to email server due to {e}")
        text = message.as_string()

        #For loop to send to all recipients.
        try:
            server.sendmail(self.from_email,self.to_emails,text)
            logging.info(f'{datetime.now()}: Password reset email has been sent successfully to {self.to_emails}')
        except smtplib.SMTPException as e:
            logging.error(f"{datetime.now()} : Error sending email to email {self.to_emails}  due to {e}")
            server.quit()
            time.sleep(10)
        
        
        
        