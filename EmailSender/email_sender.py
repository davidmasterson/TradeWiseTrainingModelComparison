
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

from datetime import datetime, date
from database import user_DAOIMPL
import base64
import logging





# Get environment variables from aws 


def send_email_of_closed_positions(opens, closes, user_id):
    

    with open("static/images/MTT_logo.jpg", "rb") as image_file:
        base64_logo = base64.b64encode(image_file.read()).decode()
    email_sender_account = os.getenv('EMAIL_ADDRESS')
    smtp_port = os.getenv('SMTP_PORT')
    smtp_server = os.getenv('SMTP_SERVER')
    email_sender_user_name = os.getenv('EMAIL_SENDER_USER_NAME')
    email_password = os.getenv('EMAIL_PASSWORD')
    user = user_DAOIMPL.get_user_by_user_id(user_id)
    user_email = user[3]
    username = user[4]
    to_emails = [user_email]
    
    content = f"""
        <html>
            <body>
                <div style="text-align: left;">
                    <img src="data:image/jpeg;base64,{base64_logo}" alt="Company Logo" style="width: 0.5in; height: 0.5in; margin-bottom: 20px;">
                </div>
                <div>
                <p>Good evening {username},</p>
                <p>Please see the below listed positions that were purchased and closed during market hours on {date.today()}.</p>
                <h3>Opened Positions</h3>
                <table border="1" cellspacing="0" cellpadding="5">
                    <tr>
                        <th>SYMBOL</th>
                        <th>QTY</th>
                        <th>P-PRICE</th>
                        <th>TOTAL-P</th>
                    </tr>
                    {''.join([f"<tr><td>{op['symbol']}</td><td>{op['qty']}</td><td>${op['purchase_price']}</td><td>${op['total_purchase']}</td></tr>" for op in opens])}
                </table>
                <h3>Closed Positions</h3>
                <table border="1" cellspacing="0" cellpadding="5">
                    <tr>
                        <th>SYMBOL</th>
                        <th>QTY</th>
                        <th>P-PRICE</th>
                        <th>TOTAL-P</th>
                        <th>S-PRICE</th>
                        <th>TOTAL-S</th>
                        <th>RETURN</th>
                        <th>ROI</th>
                    </tr>
                    {''.join([f"<tr><td>{close['symbol']}</td><td>{close['qty']}</td><td>${close['purchase_price']}</td><td>${close['total_purchase']}</td><td>${close['sell_price']}</td><td>${close['total_sell']}</td><td>${close['actual_return']}</td><td>{close['percentroi']}%</td></tr>" for close in closes])}
                </table>
                <p>Thank you for your continued support.</p>
                <p>Respectfully,<br>
                David Masterson<br>
                C.E.O and Founder Master Trade Tools, Inc.</p>
                <small><p><i>1620 Lincoln Drive.</br>
                Galena, KS 66739</i></p></small>
                </div>
            </body>
        </html>
        """
    
    message = MIMEMultipart()
    message["From"] = email_sender_account
    message["To"] = to_emails
    message['Subject'] = f"Daily closed and purchased positions {date.today()}"
    message.attach(MIMEText(content, 'html'))
    
    
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
    logging.debug(f'Successfully sent daily email to {user_email}')