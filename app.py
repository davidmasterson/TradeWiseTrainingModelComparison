import sys
from flask import Flask, render_template, request, jsonify, Response, redirect, url_for, flash
import logging
from Hypothetical_Predictor import CSV_Writer
import Selenium.selenium_file
import alpaca_request_methods
import model_trainer_predictor_methods
from Models import preprocessing_script, metric, trade_setting, user_preferences, model_metrics_history, user, model, training_script, dataset, recommendation_script
# from asyncio import sleep
import os
import Hypothetical_Predictor
import subprocess
from database import (metrics_DAOIMPL, manual_metrics_DAOIMPL,  transactions_DAOIMPL, user_preferences_DAOIMPL, preprocessing_scripts_DAOIMPL, 
                      model_metrics_history_DAOIMPL, models_DAOIMPL, training_scripts_DAOIMPL, dataset_DAOIMPL, recommendation_scripts_DAOIMPL,
                      transaction_model_status_DAOIMPL, daily_balance_DAOIMPL)
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
import threading
import pandas as pd
from Purchaser import  purchaser
import queue
import order_methods
import requests
from flask_cors import CORS
import asyncio
from datetime import datetime
import json
from authlib.integrations.flask_client import OAuth
import cProfile
from collections import defaultdict
from HistoricalFetcherAndScraper import scraper
import time
from YahooFinance import yahoo_finance_api_methods


app = Flask(__name__)



CORS(app, supports_credentials=True)
# Check if the environment is production
if os.getenv('FLASK_ENV') == 'production':
    app.config['SESSION_COOKIE_SECURE'] = True
else:
    app.config['SESSION_COOKIE_SECURE'] = False

app.secret_key = os.getenv('SECRET')

# Global variables to track progress
progress = 0
result_queue = queue.Queue()

# security measures against crosssite scripting.
csrf = CSRFProtect(app)

# Define log directory and ensure it exists
log_dir = "/home/ubuntu/TradeWiseTrainingModelComparison/logs"
os.makedirs(log_dir, exist_ok=True)  # Create the directory if it doesn't exist

# Define the log file path
log_file = os.path.join(log_dir, "app.log")

# Set up logging
# logging.basicConfig(
#     filename='app.log',
#     level=logging.INFO,
#     format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
#     datefmt='%Y-%m-%d %H:%M:%S'
# )
# # Attach logging to Flask's logger and configure it to log to the console as well
# app.logger.addHandler(logging.StreamHandler(sys.stdout))  # Outputs logs to console
# app.logger.setLevel(logging.INFO)  # Logs errors only


# #Set up Google OAuth2.0
oauth = OAuth(app)
oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',  # Fetch metadata
    client_kwargs={
        'scope': 'openid email profile'
    },
    api_base_url='https://www.googleapis.com/oauth2/v1/',  # Set base URL
    userinfo_endpoint='https://www.googleapis.com/oauth2/v3/userinfo'  # Explicitly define userinfo endpoint
)



@app.before_request
def log_request():
    logging.info(f"Incoming request: {request.method} {request.url}")

#Public Homepage
@app.route('/', methods=['GET'])
def home():
    # Check if the user is logged in
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
    if session.get('google_token'):
        return redirect(url_for('dashboard'))
    return render_template('home.html')  # Renders new homepage with Sign In and Sign Up buttons


# Authenticated user's homepage
@app.route('/index', methods=['GET'])
def index():
    if session.get('logged_in'):
        
        return render_template('index.html')
    return redirect(url_for('home'))

# ------------------------------------------------------------------START USER MANAGEMENT -----------------------------------------------------------------
import bcrypt
from database import user_DAOIMPL, reset_password_DAOIMPL, roles_DAOIMPL, user_roles_DAOIMPL, trade_settings_DAOIMPL
from Models import user, password_resets, email_sender
from flask import session, abort
from Models import user, user_role
from flask_login import LoginManager, login_user, login_required, current_user

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return user_DAOIMPL.get_user_by_user_id(user_id)


def require_roles(*roles):
    def decorator(f):
        def wrapped(*args, **kwargs):
            user_role = user.User.get_current_user_role(request)
            if user_role not in roles:
                abort(403) #forbidden
            return f(*args, **kwargs)
        return wrapped
    return decorator

# New sign-up route (already included in your existing routes)
@app.route('/submit_signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get the form data
        first_name = request.form.get('first')
        last_name = request.form.get('last')
        user_name = request.form.get('user')
        user_name = user_name.strip(' ')
        password = request.form.get('password')
        password = password.strip(' ')
        email = request.form['email']
        alpaca_key = request.form['alpaca_key']
        alpaca_secret = request.form['alpaca_secret_key']
        alpaca_endpoint = request.form['alpaca_endpoint']
        minpps = request.form['minpps']
        maxpps = request.form['maxpps']
        risk = request.form['risk']
        conf_thresh = request.form['conf_thresh']
        mints = request.form['mints']
        maxts =  request.form['maxts']
        password = user.User.hash_password(password)
        #check for existing user
        user_found = user_DAOIMPL.get_user_by_username(user_name)
        if user_found:
            error_message = 'Please choose a different user_name.'
            return render_template('signup.html', error_message=error_message)
        new_user = user.User(first=first_name, last=last_name, user_name=user_name, password=password, email=email, alpaca_key=alpaca_key, alpaca_secret=alpaca_secret, alpaca_endpoint=alpaca_endpoint)
        admin_id = user_DAOIMPL.get_user_by_username('shadow073180')
        if admin_id:
            admin_id = admin_id[0]['id']
        new_user_id = user_DAOIMPL.insert_user(new_user)
        user_sign_up_trade_settings = trade_setting.TradeSetting(new_user_id,minpps,maxpps,risk,conf_thresh,mints,maxts)
        trade_settings_DAOIMPL.insert_trade_setting(user_sign_up_trade_settings)
        role_id = roles_DAOIMPL.get_role_id_by_role_name('retail',admin_id)
        new_user_roll = user_role.UserRole(new_user_id,role_id)
        user_roles_DAOIMPL.insert_user_role(new_user_roll, admin_id)
        return render_template('login.html', success = 'Your account was created successfully!')  # Redirect to login page after successful sign-up
    return render_template('signup.html')

@app.route('/google_callback')
def google_callback():
    try:
        # Handle Google OAuth callback
        token = oauth.google.authorize_access_token()
        user_info = oauth.google.get('userinfo').json()

        if not user_info or not user_info.get('email'):
            flash('Google authentication failed. Please try again.', 'error')
            return redirect(url_for('login'))

        google_email = user_info['email']
        google_name = user_info['name']

        # Check if the user exists in your database
        user_data = user_DAOIMPL.get_user_by_email(google_email)
        if user_data:
            # User exists, log them in
            session['logged_in'] = True
            session['user_id'] = user_data[0]
            session['user_name'] = user_data[4]
            session['google_token'] = token
        else:
            # User doesn't exist, auto-register or redirect to registration
            user_name = google_email.split('@')[0]  # Default username from email
            new_user = user.User(first=google_name.split()[0], last=google_name.split()[-1],
                                  user_name=user_name, email=google_email, password=None)
            new_user_id = user_DAOIMPL.insert_user(new_user)

            # Set session variables for the new user
            session['logged_in'] = True
            session['user_id'] = new_user_id
            session['user_name'] = user_name
            session['google_token'] = token

        # Redirect to dashboard after successful login
        return redirect(url_for('dashboard'))

    except Exception as e:
        logging.error(f"Google OAuth Callback Error: {e}")
        flash('An error occurred during Google authentication. Please try again.', 'error')
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle traditional username/password login
        username = request.form.get('username')
        username = username.strip(' ')
        password = request.form.get('password')
        password = password.strip(' ')

        if not username or not password:
            return render_template('login.html', error='Username and password are required.')

        try:
            user_data = user_DAOIMPL.get_user_by_username(username)
            if not user_data:
                return render_template('login.html', error='Invalid username or password.')
            
            try:
                user_data_id = user_data[0]['id']
                user_data = user_data[0]
            except:
                user_data = user_data

            if bcrypt.checkpw(password.encode('utf-8'), user_data['password'].encode('utf-8')):
                # Set session variables for traditional login
                session['logged_in'] = True
                session['user_name'] = user_data['user_name']
                session['user_id'] = user_data['id']
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html', error='Invalid username or password.')
        except Exception as e:
            logging.error(f"Login error: {e}")
            return render_template('login.html', error='An unexpected error occurred. Please try again.')

    # For GET requests, include Google OAuth login option
    return render_template('login.html', google_login_url=url_for('google_login'))


@app.route('/google_login')
def google_login():
    """Redirects the user to Google's OAuth authorization page."""
    return oauth.google.authorize_redirect(url_for('google_callback', _external=True))




@app.route('/update_user_api_keys', methods=['POST'])
def update_api_keys():
    
    # Get form data and validate
    username = request.form.get('user')
    password = request.form.get('password')
    alpaca_key = request.form.get('alpaca_key')
    alpaca_secret_key = request.form.get('alpaca_secret_key')
    alpaca_endpoint = request.form.get('alpaca_endpoint')
    # Fetch user from the database
    try:
        conn = alpaca_request_methods.create_alpaca_api_during_api_key_resub(alpaca_key,alpaca_secret_key,alpaca_endpoint)
        account = conn.get_account()
        if account:
            user_data = user_DAOIMPL.get_user_by_username(username)[0]
            logging.info( f'this is the {user_data}')
            if user_data is not None:
                if bcrypt.checkpw(password.encode('utf-8'), user_data['password'].encode('utf-8')):
                    session['logged_in'] = True
                    session['user_name'] = user_data['user_name']
                    session['user_id'] = user_data['id']
                    #Try users Alpaca API Keys
                    user_DAOIMPL.update_user_alpaca_keys(alpaca_key,alpaca_secret_key,user_data['id'])
                    # Start WebSocket using the user_id directly
                    try:
                        username = user_data['user_name']
                        user_id = user_data['id']
                        url = url_for('start_websocket_route', username=username, user_id=user_id, _external=True)
                        response = requests.get(url)
                        logging.info(f"WebSocket initiation response: {response.status_code}")
                    except Exception as e:
                        logging.error(f"Failed to start WebSocket: {e}")
                    return redirect(url_for('dashboard'))
                    
            else:
                return render_template('login.html', error='Invalid username or password')
    except:
        render_template('APIKeys_resubmission.html', user=username, first=user_data['first'], last=user_data['last'], email=user_data['email'],
                        error = "Your alpaca API keys do not work, please resubmit the correct alpaca key and alpaca secret key. ")
    
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        if email:
            user = user_DAOIMPL.get_user_by_email_address(email)
            if not user:
                error = 'A user with this email address does not exist'
                return render_template('login.html', error=error)
            reset_token = password_resets.PasswordResets(None, None, None, None)
            token = reset_token.create_reset_token(user[0]['id'])
            new_email_sender = email_sender.EmailSender([email])
            new_email_sender.send_reset_email(token)
            success = 'Password reset email has been sent'
            return render_template('login.html', success=success)
    message = 'Please check your email. If an account is associated with this email address, you will receive a password reset email.'
    return render_template('forgot_password.html', message=message)
    

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    password_rst = password_resets.PasswordResets(None, None, None, None)
    user_id = reset_password_DAOIMPL.get_user_id_by_token(token)

    if user_id is None:
        error = 'Invalid or expired token'
        return render_template('login.html', error=error)
    if not password_rst.validate_token(user_id[0],token):
        error = 'Invalid or expired token'
        return render_template('login.html', error=error)

    if request.method == 'POST':
        user_id = reset_password_DAOIMPL.get_user_id_by_token(token)
        new_password = request.form.get('password')
        hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
        user_DAOIMPL.update_user_password(user_id[0], hashed_password)
        password_reset_instance = password_resets.PasswordResets(None, None, None, None)
        password_resets.PasswordResets.invalidate_password_reset_token(password_reset_instance,user_id[0])
        success = "Password has been reset successfully."
        return render_template('login.html', success=success)

    return render_template('reset_password.html', token=token)  # Display password reset form

@app.route('/user_profile', methods=['GET', 'POST'])
def user_profile():
    if session.get('logged_in'):
        user_id = session.get('user_id')
        last_5 = transactions_DAOIMPL.get_project_training_most_recent_5_transactions_for_user(user_id)
        user = user_DAOIMPL.get_user_by_username(session.get('user_name'))[0]
        conn = alpaca_request_methods.create_alpaca_api(session.get('user_name'))
        account = conn.get_account()
        metric = metrics_DAOIMPL.get_last_metric_for_user(user_id)
        open_pos = transactions_DAOIMPL.get_open_transactions_for_user(user_id)
        if metric:
            profit = metric[6]
            profit = float(profit) if profit else 0
            loss = float(metric[7])
            loss = float(loss) if loss else 0
            total_profit = profit + loss
        else:
            total_profit = 0.00
            
        # Modify current positions with new current price data and p and l
        if open_pos:
            positions_list = []
            for pos in open_pos:
                current_price = alpaca_request_methods.get_symbol_current_price(pos[1])
                pandl = round(float(current_price * int(pos[4])) - float(pos[5]),2)
                yesterday_close = alpaca_request_methods.get_symbol_previous_close(pos[1])
                positions_list.append({
                    'id': pos[0],
                    'symbol': pos[1],
                    'date_purchased': pos[2],
                    'pricepershare' : round(pos[3],2),
                    'qty' : pos[4],
                    'total_purchase': round(pos[5],2),
                    'expected': round(pos[11],2),
                    'tp1': round(pos[14],2),
                    'sop': round(pos[15],2),
                    'sector': pos[19],
                    'current_price' : round(current_price,2),
                    'current_pl' : pandl,
                    'yesterdays_close': yesterday_close
                })
                
        
        balances = daily_balance_DAOIMPL.get_daily_balances_for_user(user_id)
        if balances:
            s_p_index_values = []
            vanguard_index_values = []
            dates = [x[1] for x in balances]
            daily_balances = [x[2] for x in balances]
            for i in dates:
                s_p_index_values.append(yahoo_finance_api_methods.get_s_and_p_value_on_specific_date(i))
                vanguard_index_values.append(yahoo_finance_api_methods.get_vanguard_value_on_specific_date(i))
            
            # function to normalize for overlay
            def normalize_values(base, start_value, end_value):
                return round((end_value/start_value) * base, 2) 
            my_norm = []
            sp_norm = []
            vang_norm = []
            dates = [x.strftime("%Y-%m-%d") for x in dates]
            # get normalized values for indexes and my balance values
            for x in range(0,len(daily_balances)):
                my_norm.append(normalize_values(100,daily_balances[0], daily_balances[x]))
                sp_norm.append(normalize_values(100, s_p_index_values[0], s_p_index_values[x]))
                vang_norm.append(normalize_values(100, vanguard_index_values[0], vanguard_index_values[x]))
        else:
            dates, my_norm, sp_norm, vang_norm = None, None, None, None
        equity = float(account.equity)
        cash = float(account.cash)
        sp_value_now = yahoo_finance_api_methods.get_open_and_close_for_s_and_p_value_now()
        nyse_value_now = yahoo_finance_api_methods.get_open_and_close_for_NYSE_value_now()
        nasdaq_value_now = yahoo_finance_api_methods.get_open_and_close_for_NASDAQ_value_now()
        print([close['yesterdays_close'] for close in positions_list], [close['pricepershare'] for close in positions_list])
        return render_template('user_profile_page.html', last_5=last_5, user=user, equity=equity, cash=cash, profit_loss=round(total_profit,2),
                               open_pos = positions_list, sp_value_now=sp_value_now, nyse_value_now=nyse_value_now,nasdaq_value_now=nasdaq_value_now,
                               dates=dates, sp_norm=sp_norm, vang_norm=vang_norm,my_norm=my_norm)
    return redirect(url_for('home'))  # Redirect to homepage if not logged in

@app.route('/sell_position', methods=['POST'])
def sell_position():
    if session.get('logged_in'):
        user_id = user.User.get_id()
        user_obj = user_DAOIMPL.get_user_by_user_id(user_id)
        username = user_obj[4]
        symbol = request.form.get('trans_symbol')
        current_price = request.form.get('trans_price')
        current_price = round(float(current_price),2)
        quantity = request.form.get('trans_qty')
        quantity = int(quantity)
        if not all([user_id, symbol, current_price, quantity]):
            flash("Missing required form data", "error")
            return redirect(url_for('user_profile'))
            
        order_dict = {
            'symbol': symbol,
            'qty': quantity,
            'side': 'sell',
            'type': 'limit',
            'tif': 'day',
        }
        message = order_methods.submit_limit_order(username,order_dict )
        flash(message)  
        return redirect(url_for('user_profile'))

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if session.get('logged_in'):
        user_id = session.get('user_id')
        new_email = request.form.get('email')
        new_password = request.form.get('password')

        # Validate and sanitize inputs
        if new_email:
            try:
                if user_DAOIMPL.update_user_email(user_id, new_email): 
                    flash('Email updated successfully!', 'success')
            except Exception as e:
                flash(f'Error updating email: {str(e)}', 'error')
        
        if new_password:
            try:
                hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
                if user_DAOIMPL.update_user_password(user_id, hashed_password):
                    flash('Password updated successfully!', 'success')
            except Exception as e:
                flash(f'Error updating password: {str(e)}', 'error')
        
        return redirect(url_for('user_profile')) # Reload profile page

    return redirect(url_for('home')) # Redirect if not logged in

@app.route('/update_trade_settings', methods=['GET', 'POST'])
def update_trade_settings():
    from Models import trade_setting
    id = user.User.get_id()
    if request.method == 'POST':
        # Assume validation and sanitation logic is implemented
        new_settings = {
            'min_price': request.form.get('min_price'),
            'max_price': request.form.get('max_price'),
            'risk_tolerance': request.form.get('risk_tolerance'),
            'confidence_threshold': request.form.get('confidence_threshold'),
            'min_total' : request.form.get('min_total'),
            'max_total' : request.form.get('max_total')
        }
        trade_settings = trade_settings_DAOIMPL.get_trade_settings_by_user(id)
        new_trade_settings = trade_setting.TradeSetting(id,new_settings['min_price'],new_settings['max_price'],new_settings['risk_tolerance'],new_settings['confidence_threshold'],
                                                        new_settings['min_total'], new_settings['max_total'])
        trade_settings_DAOIMPL.update_trade_settings_for_user(new_trade_settings,trade_settings[0])
        flash('Trade settings updated successfully!', 'success')
        return redirect(url_for('update_trade_settings'))

    # Load existing settings to display in the form
    settings = trade_settings_DAOIMPL.get_trade_settings_by_user(id)
    return render_template('trade_settings.html', trade_settings=settings)

# -------------------------------------------------------ADMINISTRATION USER MANAGEMENT ----------------------------------------------------------------------
@app.route('/admin_panel', methods = ['GET'])
def admin_panel():
    user_id = user.User.get_id()
    if not user_role.UserRole.check_if_admin(user_id):
        abort(403) #not authorized
    message = 'This is a protected admin-only area. Your actions are being logged.'
    total_profit = round(metrics_DAOIMPL.get_all_profits_for_all_users(),2)
    total_loss = round(metrics_DAOIMPL.get_all_loss_for_all_users(),2)
    total_number_of_users = user_DAOIMPL.get_total_number_of_users()
    total_investment_cash = sum([round(float(bal[2]),2) for bal in daily_balance_DAOIMPL.get_first_balance_for_specific_endpoint('https://api.alpaca.markets')])
    total_investment_practice = sum([round(float(bal[2]),2) for bal in daily_balance_DAOIMPL.get_first_balance_for_specific_endpoint('https://paper-api.alpaca.markets')])
    return render_template('admin_panel.html', message=message, total_profit=total_profit, total_loss=total_loss,
                           total_number_of_users=total_number_of_users, total_investment_cash=total_investment_cash,
                           total_investment_practice = total_investment_practice)

@app.route('/admin/users', methods=['GET'])
def admin_users():
    id = user.User.get_id()
    if not user_role.UserRole.check_if_admin(id):
        abort(403) #deny access
    users = roles_DAOIMPL.get_all_users_and_roles(id) #get all users from database
    return render_template('admin_users.html', users=users)

@app.route('/admin/assign_role', methods=['POST'])
def assign_role():
    user_id = user.User.get_id()
    if not user_role.UserRole.check_if_admin(user_id):
        abort(403) # deny access
    user_id = request.form['user_id']
    new_role = request.form['role']
    user_roles_DAOIMPL.update_user_role(user_id, new_role, current_user)
    return redirect(url_for('admin_users'))

from flask import Flask, render_template, request, redirect, url_for, flash

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if not user_role.UserRole.check_if_admin(user_id):
        abort(403)
    if request.method == 'POST':
        # Handle the form submission
        first = request.form['first']
        last = request.form['last']
        email = request.form['email']
        user_name = request.form['user_name']
        password = request.form['password']  
        alpaca_key = request.form['alpaca_key']
        alpaca_secret = request.form['alpaca_secret']
        
        # Assume function to update user exists
        new_user = user.User(first=first,last=last,email=email,user_name=user_name, password=password,alpaca_key=alpaca_key, alpaca_secret=alpaca_secret)
        update_success = user_DAOIMPL.update_user(new_user,user_id)
        if update_success:
            flash('User updated successfully!', 'success')
            return redirect(url_for('admin_users' ))
        else:
            flash('Failed to update user.', 'error')
            return render_template('user_update.html', user=[user_id, first, last, email,user_name, password,  alpaca_key, alpaca_secret])
    
    # GET request: Fetch user data and populate the form
    user_details = user_DAOIMPL.get_user_by_user_id(user_id)  # This function needs to return a list of user attributes
    if user_details:
        return render_template('user_update.html', user=user_details)
    else:
        flash('User not found!', 'error')
        return redirect(url_for('admin_users'))


@app.route('/delete_user', methods=['POST'])
def delete_user():
    id = user.User.get_id()
    user_name = request.form.get('user_name')
    user_for_deletion = user_DAOIMPL.get_user_by_username(user_name)
    if user_for_deletion:
        user_for_deletion = user_for_deletion[0]
    if not user_for_deletion:
        message = f'User by that username {user_name} does not exist'
        return render_template('admin_users.html', error=message)
    # delete user_role first
    user_role = user_roles_DAOIMPL.get_user_role_id_by_user_id(user_for_deletion['id'], id)
    user_roles_DAOIMPL.delete_user_role(user_role, id)
    # delete user
    user_DAOIMPL.delete_user(user_for_deletion['id'])
    message = f'User {user_name} successfully deleted by user {id}'
    return render_template('admin_users.html', success=message)

@app.route('/admin/assign_roles', methods=['GET', 'POST'])
def assign_roles():
    requestor_id = user.User.get_id()
    if not user_role.UserRole.check_if_admin(requestor_id):
        abort(403)
    if request.method == 'POST':
        user_ids = request.form.getlist('user_ids[]')  # Gets list of user IDs
        roles = request.form.getlist('roles[]')
        
        for user_id, role in zip(user_ids, roles):
            user_id = int(user_id)
        # Process each user and role
            if update_user_role(user_id, role):       
                flash('Role updated successfully!', 'success')
            else:
                flash(f'Unable to update role to {role} for user {user_id}', 'error')              
        return redirect(url_for('assign_roles'))
        
    users = roles_DAOIMPL.get_all_users_and_roles(requestor_id)
    roles = roles_DAOIMPL.get_all_roles(requestor_id)
    if roles:
        print(roles)
    return render_template('assign_roles.html', users=users, roles=roles)
   

def update_user_role(user_id, role):
    try:
        requestor_id = user.User.get_id()
        role_id = roles_DAOIMPL.get_role_id_by_role_name(role, requestor_id)
        user_roles_DAOIMPL.update_user_role(user_id, role_id, requestor_id)
        return True
    except Exception as e:
        print(f"Error updating user role: {str(e)}")
        return False

# ---------------------------------------------------END ADMINISTRATION USER MANAGEMENT--------------------------------------------------------------------------------------
# ---------------------------------------------------END USER MANAGEMENT -------------------------------------------------------------------------------------
# ---------------------------------------------------------MODEL TRAINERS -------------------------------------------------------------------------------------

import subprocess
import tempfile
import pickle
import json
from database import models_preprocessing_scripts_DAOIMPL, models_training_scripts_DAOIMPL
from datetime import datetime
from flask import flash, redirect, url_for
from Models import preprocessing_script, training_script, metric, models_preprocessing_scripts, models_training_scripts

@app.route('/train_model/<model_name>', methods=['POST'])
def train_model(model_name):
    try:
        
        project_root = "/home/ubuntu/TradeWiseTrainingModelComparison"
        # Retrieve and validate form data
        user_id = user.User.get_id()
        model_name = request.form.get('model_name')
        model_id = models_DAOIMPL.get_model_id_for_model_by_model_name(model_name)
        preprocessing_script_id = request.form.get('preprocessed_data')
        training_script_id = request.form.get('training_script')
        dataset_id = request.form.get('dataset_data')
        if not all([preprocessing_script_id, training_script_id, dataset_id, model_id]):
            flash("Missing required form data: preprocessing_script_id, training_script_id, or dataset_id.", "error")
            return redirect(url_for('dashboard'))
        preprocessing_script_id = int(preprocessing_script_id)
        training_script_id = int(training_script_id)
        model_id = int(model_id)
        
        # Insert or update model_preprocessing_script union table entry
        current_exists = models_preprocessing_scripts_DAOIMPL.get_entry_by_model_id(model_id)
        new_modppscript = models_preprocessing_scripts.ModelPreProcessingScripts(model_id,preprocessing_script_id)
        if current_exists:
            models_preprocessing_scripts_DAOIMPL.update_models_preprocessing_script_table(new_modppscript)
        else:
            models_preprocessing_scripts_DAOIMPL.insert_into_models_preprocessing_scripts_table(new_modppscript)
       
        # Insert or update models_training_script union table entry
        current_exists = models_training_scripts_DAOIMPL.get_entry_by_model_id(model_id)
        new_mod_trainscript = models_training_scripts.ModelsTrainingScripts(model_id,training_script_id)
        if current_exists:
            models_training_scripts_DAOIMPL.update_models_training_script_table(new_mod_trainscript)
        else:
            models_training_scripts_DAOIMPL.insert_into_models_training_scripts_table(new_mod_trainscript)
        
        model_type = models_DAOIMPL.get_model_name_for_model_by_model_id(model_id)
        closed_transactions = transactions_DAOIMPL.get_all_closed_unprocessed_transactions_for_user(user_id)
        
        result = preprocessing_script.Preprocessing_Script.retrainer_preprocessor(preprocessing_script_id, project_root, dataset_id, user_id, model_id, closed_transactions, model_name)
        
        
        # Read preprocessed data from ouput path to ouput a preprocessed data object for use with training script    
        training_script.TrainingScript.model_trainer(training_script_id,preprocessing_script_id, model_id, user_id, model_name, project_root)
        flash('Training has completed successfully as well as new metrics entry.', 'success')   
        return redirect(url_for('dashboard'))

    except Exception as e:
        logging.error(f"Unexpected error in train_model route: {e}")
        flash("An unexpected error occurred during training.", "error")
        return redirect(url_for('dashboard'))

@app.route('/upload_models', methods = ['GET','POST'])
def upload_models():
    import pickle
    from Models import transaction
    if user.User.check_logged_in():
        user_id = user.User.get_id()
        if request.method == 'POST':
            model_name = request.form['model_name']
            model_description = request.form['model_description']
            ppscript = request.form['preprocessing_script']
            dataset = request.form['dataset']
            tscript = request.form['training_script']
            if model_name and model_description and ppscript and tscript and dataset:
                ppscript = int(ppscript)
                dataset = int(dataset)
                tscript = int(tscript)
            
            # Save model without binary model to database.
            new_model = model.Model(model_name, model_description, model_data = None, user_id=user_id, selected=0)
            model_id = models_DAOIMPL.insert_model_into_models_for_user(new_model)
            
            # Insert or update model_preprocessing_script union table entry
            current_exists = models_preprocessing_scripts_DAOIMPL.get_entry_by_model_id(model_id)
            new_modppscript = models_preprocessing_scripts.ModelPreProcessingScripts(model_id,ppscript)
            if current_exists:
                models_preprocessing_scripts_DAOIMPL.update_models_preprocessing_script_table(new_modppscript)
            else:
                models_preprocessing_scripts_DAOIMPL.insert_into_models_preprocessing_scripts_table(new_modppscript)
        
            # Insert or update models_training_script union table entry
            current_exists = models_training_scripts_DAOIMPL.get_entry_by_model_id(model_id)
            new_mod_trainscript = models_training_scripts.ModelsTrainingScripts(model_id,tscript)
            if current_exists:
                models_training_scripts_DAOIMPL.update_models_training_script_table(new_mod_trainscript)
            else:
                models_training_scripts_DAOIMPL.insert_into_models_training_scripts_table(new_mod_trainscript)
            closed_transactions = transactions_DAOIMPL.get_all_closed_unprocessed_transactions_for_user(user_id)
            project_root = "/home/ubuntu/TradeWiseTrainingModelComparison"
            # create a preprocessed data object
            try:
                result = preprocessing_script.Preprocessing_Script.retrainer_preprocessor(ppscript,project_root,dataset,user_id,model_id, closed_transactions, model_name)
                
            
                # Read preprocessed data from ouput path to ouput a preprocessed data object for use with training script    
                training_script.TrainingScript.model_trainer(tscript,ppscript, model_id, user_id, model_name, project_root)
                
                
            # Notify user of successful model creation, and delete temporary transaction.
                flash('Model has been uploaded successfully','info')
                transactions_DAOIMPL.delete_transaction(transaction_id)
                return redirect(url_for('upload_models'))
            except Exception as e:
                logging.error(f'Unable to add model due to {e}')
                return 

    # If GET request, render the upload form
        models = models_DAOIMPL.get_models_for_user_by_user_id(user_id)
        training_scripts = training_scripts_DAOIMPL.get_all_training_scripts_for_user(user_id)
        preprocessing_scripts = preprocessing_scripts_DAOIMPL.get_preprocessing_scripts_for_user(user_id)
        datasets = dataset_DAOIMPL.get_datasets_by_user_id(user_id)
        if models:
            models = models
        return render_template('models.html', models=models, training_scripts=training_scripts, preprocessing_scripts=preprocessing_scripts,
                               datasets=datasets)
        
@app.route('/delete_model', methods=['POST'])
def delete_model():
    user_id = user.User.get_id()
    model_id = request.form.get('model_id')
    model_id = int(model_id)
    model_name = models_DAOIMPL.get_model_name_for_model_by_model_id(model_id)
    try:
        models_DAOIMPL.delete_model_by_id(model_id)
        
    except Exception as e:
        logging.error(f'Unable to delete model {model_name} due to {e}')
        flash(f'Unable to delete model {model_name}')
    try:
        transaction_model_status_DAOIMPL.delete_specific_model_entries_for_user(model_name, user_id)
    except Exception as e:
        logging.error(f'Unable to remove model {model_name} entries in tms table due to {e}')
        flash(f'Unable to remove entries for model {model_name}')
    flash(f"ML Model {model_name} has been deleted.")
    return redirect(url_for('upload_models'))
       
    

# ------------------------------------------------------------END MODEL --------------------------------------------------------------------------

# @app.route('/index_comparisons', methods=['GET'])
# def index_comparisons():
#     from YahooFinance import yahoo_finance_api_methods
#     if user.User.check_logged_in():
#         user_id = user.User.get_id()
#         balances = daily_balance_DAOIMPL.get_daily_balances_for_user(user_id)
#         if balances:
#             s_p_index_values = []
#             vanguard_index_values = []
#             dates = [x[1] for x in balances]
#             daily_balances = [x[2] for x in balances]
#             for i in dates:
#                 s_p_index_values.append(yahoo_finance_api_methods.get_s_and_p_value_on_specific_date(i))
#                 vanguard_index_values.append(yahoo_finance_api_methods.get_vanguard_value_on_specific_date(i))
            
#             # function to normalize for overlay
#             def normalize_values(base, start_value, end_value):
#                 return round((end_value/start_value) * base, 2) 
#             my_norm = []
#             sp_norm = []
#             vang_norm = []
#             dates = [x.strftime("%Y-%m-%d") for x in dates]
#             # get normalized values for indexes and my balance values
#             for x in range(0,len(daily_balances)):
#                 my_norm.append(normalize_values(100,daily_balances[0], daily_balances[x]))
#                 sp_norm.append(normalize_values(100, s_p_index_values[0], s_p_index_values[x]))
#                 vang_norm.append(normalize_values(100, vanguard_index_values[0], vanguard_index_values[x]))
#         else:
#             dates, my_norm, sp_norm, vang_norm = None, None, None, None
#         sp_value_now = yahoo_finance_api_methods.get_open_and_close_for_s_and_p_value_now()
#         nyse_value_now = yahoo_finance_api_methods.get_open_and_close_for_NYSE_value_now()
#         nasdaq_value_now = yahoo_finance_api_methods.get_open_and_close_for_NASDAQ_value_now()
#         return render_template('index_comparisons.html', my_norm=my_norm, dates=dates, sp_norm=sp_norm, 
#                                vang_norm=vang_norm,sp_value_now=sp_value_now, 
#                                nyse_value_now=nyse_value_now,nasdaq_value_now=nasdaq_value_now)
#     return redirect(url_for('home'))


from flask import request, redirect, url_for, flash, render_template
import pickle
import os
from datetime import datetime
import tempfile
import subprocess

def validate_preprocessed_data(data):
    structure = data.get('structure')
    if structure == 'train_test_split':
        required_keys = ['X_train', 'X_test', 'y_train', 'y_test', 'scaler']
    elif structure == 'scaled':
        required_keys = ['X_scaled', 'y', 'scaler']
    else:
        raise ValueError(f"Unknown data structure format: {structure}")
    return all(key in data for key in required_keys)


@app.route('/upload_preprocessing_scripts', methods=['GET', 'POST'])
def upload_preprocessing_scripts():
    if user.User.check_logged_in():
        user_id = user.User.get_id()
        if request.method == 'POST':
            # Get frontend form data
            script_name = request.form['script_name']
            description = request.form['script_description']
            script_file = request.files['script_file']
            dataset_id = int(request.form['dataset_id'])  # Get dataset ID from the form

            if script_file and script_name and description and dataset_id:
                script_content = script_file.read().decode('utf-8')
                script_content = pickle.dumps(script_content)
            try:
                # Insert script data into the database
                new_script = preprocessing_script.Preprocessing_Script(
                    script_name, description, script_content, datetime.now(), user_id, None
                )
                script_id = preprocessing_scripts_DAOIMPL.insert_preprocessing_script_for_user(new_script)
                flash('Successfully Inserted New Preprocessing Script', 'success')
                return redirect(url_for('upload_preprocessing_scripts'))
            except Exception as e:
                flash(f'Error during upload {e}','error')
        
        datasets = dataset_DAOIMPL.get_datasets_by_user_id(user_id)
        scripts = preprocessing_scripts_DAOIMPL.get_scripts_by_user_id(user_id)
        return render_template('preprocessing_scripts.html', scripts=scripts, datasets=datasets)

@app.route('/delete_ppscript', methods=['POST'])
def delete_ppscript():
    ppscript_id = request.form.get('ppscript_id')
    ppscript_id = int(ppscript_id)
    preprocessing_scripts_DAOIMPL.delete_user_preprocessing_script(ppscript_id)
    flash(f"Preprocessing Script with ID {ppscript_id} has been deleted.")
    return redirect(url_for('upload_preprocessing_scripts'))








@app.route('/upload_training_scripts', methods=['GET', 'POST'])
def upload_training_scripts():
    if user.User.check_logged_in():
        user_id = user.User.get_id()
        username = session.get('user_name')
        if request.method == 'POST':
            model_type = request.form['model_type']
            script_name = request.form['script_name']
            description = request.form['script_description']
            script_file = request.files['script_file']

            # Save the uploaded file to the database without executing
            if script_file and model_type and script_name and description:
                script_content = script_file.read().decode('utf-8')  # Read and decode script content

                # Insert script data into the database
                new_script = training_script.TrainingScript(
                    model_type=model_type,
                    script_name=script_name,
                    script_description=description,
                    script_data=script_content,
                    created_at=datetime.now(),
                    user_id=user_id
                )
                
                training_scripts_DAOIMPL.insert_training_script(new_script)
                flash('Training script uploaded successfully', 'info')
                return redirect(url_for('upload_training_scripts'))

        # If GET request, render the upload form
        scripts = training_scripts_DAOIMPL.get_all_training_scripts_for_user(user_id)
        return render_template('training_scripts.html', scripts=scripts)
    return redirect(url_for('home'))

@app.route('/delete_training_script', methods=['POST'])
def delete_training_script():
    training_script_id = request.form.get('training_script_id')
    training_script_id = int(training_script_id)
    flash(f"Training Script with ID {training_script_id} has been deleted.")
    training_scripts_DAOIMPL.delete_training_script(training_script_id)

@app.route('/select_model/<int:model_id>', methods=['POST'])
def select_model(model_id):
    user_id = user.User.get_id()
    selected = request.form.get('selected', '0')
    mod = models_DAOIMPL.get_models_for_user_by_model_id(model_id)
    if not mod or len(mod) == 0:
        logging.error(f'Model {model_id} not found for user {user_id}')
        flash('Model not found. Unable to update selected status.', 'error')
        return redirect(url_for('upload_models'))
    
    try:
        models_DAOIMPL.update_selected_status(selected,model_id)
    except Exception as e:
        logging.error(f'Unable to update selected for model {model_id} due to {e}')
        flash('Unable to select model', 'error')
        return redirect(url_for('upload_models'))
    if selected == '1':
        try:
            transaction_model_status_DAOIMPL.reselect_model_actions(mod[1],user_id)
            flash('Model status has been updated. Relevant transactions are up to date.', 'success')
            return redirect(url_for('upload_models'))
        except Exception as e:
            logging.error(f'Unable to complete required steps after model has been selected due to {e}')
            flash(f'Model {model_id} has not completed all required steps after changing selected status')
    flash(f'Successfully updated the selected status for model {mod[1]} to unselected', 'success')
    return redirect(url_for('upload_models'))       

@app.route('/upload_dataset', methods=['GET', 'POST'])
def upload_dataset():
    import pandas as pd
    
    if user.User.check_logged_in():
        user_id = user.User.get_id()

        if request.method == 'POST':
            dataset_name = request.form['dataset_name']
            description = request.form['dataset_description']
            dataset_file = request.files['dataset_file']

            if dataset_file and dataset_name and description:
                # Load dataset content into a DataFrame
                dataset_df = pd.read_csv(dataset_file)
                dataset_df = dataset_df.loc[:, ~dataset_df.columns.str.contains('^Unnamed')]
                dataset_data = pickle.dumps(dataset_df)

                # Store dataset metadata in database
                new_dataset = dataset.Dataset(
                    dataset_name=dataset_name,
                    dataset_description=description,
                    dataset_data=dataset_data,
                    uploaded_at=datetime.now(),
                    user_id=user_id
                )
                dataset_id = dataset_DAOIMPL.insert_dataset(new_dataset)

                flash('Dataset uploaded successfully.', 'info')
                return redirect(url_for('upload_dataset'))

        # Fetch datasets to display
        datasets = dataset_DAOIMPL.get_datasets_by_user_id(user_id)
        return render_template('datasets.html', datasets=datasets)

@app.route('/delete_dataset', methods=['POST'])
def delete_dataset():
    dataset_id = request.form.get('dataset_id')
    dataset_id = int(dataset_id)
    dataset_DAOIMPL.delete_dataset(dataset_id)
    flash(f"Dataset with ID {dataset_id} has been deleted.")
    return redirect(url_for('upload_dataset'))


@app.route('/upload_recommendations_scripts', methods=['GET', 'POST'])
def upload_recommendations_scripts():
    if user.User.check_logged_in():
        user_id = user.User.get_id()
        username = session.get('user_name')
        if request.method == 'POST':
            script_name = request.form['script_name']
            description = request.form['script_description']
            script_file = request.files['script_file']

            # Save the uploaded file to the database without executing
            if script_file  and script_name and description:
                script_content = script_file.read().decode('utf-8')  # Read and decode script content
                script_bin = pickle.dumps(script_content)

                # Insert script data into the database
                new_script = recommendation_script.RecommendationScript(
                    script_name,description,script_bin,user_id,datetime.now()
                )
                
                recommendation_scripts_DAOIMPL.insert_recommendation_script_for_user(new_script)
                flash('recommendation script uploaded successfully', 'info')
                return redirect(url_for('upload_recommendations_scripts'))

        # If GET request, render the upload form
        scripts = recommendation_scripts_DAOIMPL.get_recommendation_scripts_for_user(user_id)
        return render_template('recommendations_scripts.html', scripts=scripts)
    return redirect(url_for('home'))

@app.route('/delete_recommendation_script', methods=['POST'])
def delete_recommendation_script():
    recommendation_script_id = request.form.get('recommendation_script_id')
    recommendation_script_id = int(recommendation_script_id)
    flash(f"Recommendation Script with ID {recommendation_script_id} has been deleted.")
    recommendation_scripts_DAOIMPL.delete_user_recommendations_script(recommendation_script_id)
    return redirect(url_for('upload_recommendations_scripts'))
    
# -------------------------------------------------------------END MODEL TRAINING -----------------------------------------------------------------
# ----------------------------------------------------------------START ORDERS --------------------------------------------------------------------
from database import pending_orders_DAOIMPL
@app.route('/pending_orders', methods=['GET','POST'])
def pending_orders():
    if user.User.check_logged_in():
        id = user.User.get_id()
        pending_orders = pending_orders_DAOIMPL.get_all_pending_orders(id)
        if request.method == 'POST':
            order_methods.check_for_filled_orders()   
        return render_template('pending_orders.html', pending_orders=pending_orders)
    return redirect(url_for('home'))  

@app.route('/predict', methods=['POST'])
def predict():
    user_id = user.User.get_id()
    probs = model_trainer_predictor_methods.stock_predictor_using_pretrained_model(user_id)
    return render_template('stock_predictions.html', probs=probs)






@app.route('/dashboard', methods=['GET'])
def dashboard():
    if session.get('logged_in') or session.get('google_token'):
        user_id = session.get('user_id')

        # Fetch selected models separately from model metrics
        selected_models = models_DAOIMPL.get_selected_models_for_user(user_id)
        model_metrics = model_metrics_history_DAOIMPL.get_most_recent_metric_history_for_all_selected_ml_models() or []
        historical_metrics = model_metrics_history_DAOIMPL.get_all_metrics_history_for_all_selected_models_for_user_sorted_by_model(user_id) or []

        metrics_data = []
        model_names_with_metrics = {metric[0] for metric in model_metrics}

        for model in selected_models:
            model_name = model[1]
            metric = next((m for m in model_metrics if m[0] == model_name), None)
            if metric:
                top_features_str = metric[5] if isinstance(metric[5], str) else '{}'
                top_features_dict = json.loads(top_features_str)
                for feature in top_features_dict:
                    feature["Importance"] = float(feature["Importance"]) * 100
                top_features_sorted = sorted(top_features_dict, key=lambda x: x["Importance"], reverse=True)[:5]
                metrics_data.append({
                    'model_name': metric[0],
                    'accuracy': float(metric[1]),
                    'precision': float(metric[2]),
                    'recall': float(metric[3]),
                    'f1_score': float(metric[4]),
                    'top_features': top_features_sorted,
                    'timestamp': metric[6].strftime('%Y-%m-%d %H:%M:%S')
                })
            else:
                metrics_data.append({
                    'model_name': model_name,
                    'accuracy': None,
                    'precision': None,
                    'recall': None,
                    'f1_score': None,
                    'top_features': {},
                    'timestamp': "No data - Run training"
                })

        chart_data = defaultdict(lambda: {'dates': [], 'accuracy': [], 'precision': [], 'recall': [], 'f1_score': []})

        if historical_metrics:
            for entry in historical_metrics:
                model_name, accuracy, precision, recall, f1_score, _, timestamp = entry
                chart_data[model_name]['dates'].append(timestamp.strftime('%Y-%m-%d %H:%M:%S'))
                chart_data[model_name]['accuracy'].append(accuracy)
                chart_data[model_name]['precision'].append(precision)
                chart_data[model_name]['recall'].append(recall)
                chart_data[model_name]['f1_score'].append(f1_score)

        chart_data = dict(chart_data)
        preprocessed_data_options = preprocessing_scripts_DAOIMPL.get_all_preprocessed_data_for_user(user_id)
        training_script_options = training_scripts_DAOIMPL.get_all_training_scripts_for_user(user_id)
        dataset_options = dataset_DAOIMPL.get_datasets_by_user_id(user_id)

        return render_template('index.html', metrics_data=metrics_data, historical_metrics=json.dumps(chart_data),
                               preprocessed_data_options=preprocessed_data_options, training_script_options=training_script_options,
                               dataset_options=dataset_options)

    return redirect(url_for('home'))







from Models import manual_metrics
@app.route('/metrics_plots', methods=['GET'])
def plot_metrics():
    if session.get('logged_in'):
        user_id = user.User.get_id()
        metrics = metrics_DAOIMPL.get_all_metrics_for_user(user_id)
        if metrics:
            metric.Metric.plot_model_metrics(user_id)
            return render_template('metrics_plots.html', user_id=user_id)
        message = 'There are not any metrics yet!'
        return render_template('metrics_plots.html', message=message)
    return redirect(url_for('home'))



     




@app.route('/transactions', methods=['GET'])
def transactions():
    if session.get('logged_in'):
        user_id = session.get('user_id')
        transactions = transactions_DAOIMPL.get_project_training_transactions_for_user(user_id)
        return render_template('transactions.html', transactions=transactions)
    return redirect(url_for('home'))







# New logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"Unhandled exception: {e}", exc_info=True)
    # Optionally, return a custom error page to the user
    return render_template('500.html'), 500

@app.errorhandler(404)
def page_not_found(e):
    logging.warning(f"404 error: {request.url} not found")
    return render_template('404.html'), 404


def get_google_oauth_token():
    return session.get('google_token')






@app.route('/purchaser', methods=['GET', 'POST'])
def purchaser_page():
    from Finder import symbol_finder
    from Recommender import recommender
    from Purchaser import score_based_purchaser
    import ast
    from flask import session
    from threading import Thread
    from Models import recommended, progress_object
    from database import recommended_DAOIMPL, progression_DAOIMPL
    if session.get('logged_in'):
        user_name = session.get('user_name')
        user_id = user.User.get_id()
        api = alpaca_request_methods.create_alpaca_api(user_name)
        user_account = api.get_account()
        cash = float(user_account.cash)
        trade_settings = trade_settings_DAOIMPL.get_trade_settings_by_user(user_id)
        min_spend = float(trade_settings[2])
        max_spend = float(trade_settings[3])
        max_total_spend = float(trade_settings[7])
    
    

        if request.method == 'POST':
            
            # Generate recommendations and store them in the session
            #get form data from frontend
            dataset_id = request.form.get('dataset_data')
            recommendation_script_id = request.form.get('recommender_data')
            model_id = request.form.get('model_id')
            training_script = request.form.get('training_script')
            recommendation_count = request.form.get('recommendation_count')
            recommendation_count = int(recommendation_count)
            recommended_DAOIMPL.delete_all_recommended_for_user(user_id)
            # create new dataset using the recommender TODO ------
            progress_now = progression_DAOIMPL.get_recommender_progress_by_user(user_id)
            if progress_now:
                progression_DAOIMPL.update_recommender_progress(1, user_id, progress_now[0])
            else:
                new_progress = progress_object.Progress(1, user_id)
                progression_DAOIMPL.insert_recommender_progress(new_progress)
            
            progress_text = progression_DAOIMPL.get_progression_text_by_user(user_id)
            if progress_text:
                progression_DAOIMPL.update_progression_text('Getting list of tradeable positions', user_id, progress_text[0])
            else:
                progression_DAOIMPL.insert_progression_text('Getting list of tradeable positions', user_id)   
                progress_now = progression_DAOIMPL.get_recommender_progress_by_user(user_id)
                
            assets_list = symbol_finder.get_list_of_tradeable_stocks()
            progress_now = progression_DAOIMPL.get_recommender_progress_by_user(user_id)
            progression_DAOIMPL.update_recommender_progress(10, user_id, progress_now[0])
            progression_DAOIMPL.update_progression_text('Getting price data for positions', user_id, progress_now[0])
            
            assets_list = symbol_finder.fetch_price_data_concurrently(assets_list,min_spend,max_spend)
            progression_DAOIMPL.update_recommender_progress(20, user_id, progress_now[0])
            progression_DAOIMPL.update_progression_text('Sorting list', user_id, progress_now[0])
            assets_list = symbol_finder.sort_list_from_lowest_price_to_highest_price(assets_list)
            new_list = list(map(lambda x: x[0], assets_list))
            
            progression_DAOIMPL.update_progression_text('Getting recommendations based on most recent trained model',user_id, progress_now[0])
            orders = recommender.get_model_recommendations_for_recommender(new_list, recommendation_script_id, dataset_id, user_id, max_total_spend,recommendation_count,model_id, 20)
            symbols = [item['Symbol'] for item in orders]
            sectors = [item['Sector'] for item in orders]
            
            progression_DAOIMPL.update_progression_text('Processing recommended positions for display', user_id, progress_now[0])
            symbols_for_purchase = score_based_purchaser.process_symbols_for_purchase(symbols,orders, max_total_spend,sectors)
            
            for symbol, order_details in symbols_for_purchase.items():
                recommendation = recommended.Recommended(order_details['symbol'],order_details['limit_price'],order_details['confidence'],user_id)
                recommended_DAOIMPL.insert_recommendation(recommendation) 
            progression_DAOIMPL.update_progression_text(' ', user_id, progress_now[0])   
            return redirect(url_for('purchaser_page'))
                # Load recommendations from session if they exist
        recommendations = []
        orders = recommended_DAOIMPL.get_recommended_for_user(user_id)
        logging.info(orders)
        recommendations_scripts = recommendation_scripts_DAOIMPL.get_recommendation_scripts_for_user(user_id)
        models = models_DAOIMPL.get_models_for_user_by_user_id(user_id)
        datasets = dataset_DAOIMPL.get_datasets_by_user_id(user_id)
        for order in orders:
            recommendations.append( {
                'symbol': order[1],
                'limit_price': round(float(order[2]),2),
                'confidence': order[3],
                'qty': int( max_total_spend / float(order[2])),
                'sector': order[5]  
            })
        
        return render_template('purchaser.html', datasets=datasets, recommendations=recommendations, user_cash=cash, 
                               recommendations_scripts=recommendations_scripts,  
                               max_total_spend=max_total_spend, models=models, user_id=user_id
                               )
    return redirect(url_for('home'))
    
@app.route('/get_progress_text')
def get_progress_text():
    user_id = user.User.get_id()
    from database import progression_DAOIMPL
    try:
        progression_text = progression_DAOIMPL.get_progression_text_by_user(user_id)
        progression_text = progression_text[1]
    except:
        pass
    
    logging.info(f'progress_text is {progression_text}')
    # Assuming these values are updated in your stock processing logic
    return jsonify(progressText=progression_text)

@app.route('/purchase', methods=['POST'])
def purchase_stock():
    if session.get('logged_in'):
        user_id = user.User.get_id()
        # Extract form data
        symbol = request.form.get('symbol')
        limit_price = float(request.form.get('limit_price'))
        qty = int(request.form.get('qty'))
        confidence = int(request.form.get('confidence'))

        try:
            order = {
                'symbol': symbol,
                'limit_price': limit_price,
                'qty': qty,
                'side': 'buy',
                'type': 'limit',
                'tif': 'day',  # Good 'til canceled
                'confidence': confidence
            }
            # Call Alpaca's purchase method to execute the order
            message = order_methods.submit_limit_order(session.get('user_name'), order)
            
            # Flash a success message
            if "not submitted" in message:   
                flash(message, 'error')
            else:
                flash(message, 'success')
        except Exception as e:
            # Flash an error message
            flash(f"Failed to place order for {symbol}. Error: {e}", 'danger')
        
        # Redirect back to the purchaser page
        
        return redirect(url_for('purchaser_page'))
    return redirect(url_for('home'))


    
    

        
       
@app.route('/progress', methods=['GET'])
def get_progress():
    from database import progression_DAOIMPL
    user_id = session.get('user_id')
    global progress
    try:
        progress = progression_DAOIMPL.get_recommender_progress_by_user(user_id)[1] or 0
    except Exception as e:
        app.logging.error("Failed to fetch progress: %s", str(e))
        return jsonify({'error': 'Could not fetch progress'}), 500
    logging.info(f'Progress is {progress}')
    return jsonify({'progress': progress})











    
    
    


@app.route('/update_preferences', methods=['POST'])
def update_prefs():
    try:
        min_pps = request.form.get('min-price')
        max_pps = request.form.get('max-price')
        max_total = request.form.get('max-investment')
        min_total = request.form.get('min-investment')
        
        # Print or log values to check
        print(f"min_pps: {min_pps}, max_pps: {max_pps}, min_total: {min_total}, max_total: {max_total}")
        
        if None in [min_pps, max_pps, max_total, min_total]:
            raise ValueError("One of the form values is None.")
        
        min_pps = float(min_pps)
        max_pps = float(max_pps)
        max_total = float(max_total)
        min_total = float(min_total)
        
        username = session.get('user_name')
        
        # Fetch user details
        this_user = user_DAOIMPL.get_user_by_username(username)[0]
        user_id = this_user['id']

        # Update the user preferences
        user_preferences_DAOIMPL.update_user_preferences_limits_for_user(user_id, min_pps, max_pps, min_total, max_total)

        flash("Preferences updated successfully!", "success")
        
    except Exception as e:
        # Flash an error message
        flash(f"Failed to update preferences. Error: {str(e)}", "danger")
    
    return redirect(url_for('user_profile'))





# Upload preprocessing script to database
@app.route('/upload_script', methods=['POST'])
def upload_script():
    script_file = request.files['script_file']
    script_name = request.form['script_name']
    script_description = request.form['script_description']
    user_id = session.get('user_id')
    username = session.get('user_name')# Retrieve from session or login

    if script_file and script_name and script_description:
        # Read the script content
        script_content = script_file.read().decode("utf-8")

        # Create the Preprocessing_Script object
        new_script = preprocessing_script.Preprocessing_Script(
            script_name=script_name,
            script=script_content,
            user_id=user_id,
            upload_date=datetime.now(),
            script_description=script_description,
            username= username
        )

        # Save to database
        preprocessing_scripts_DAOIMPL.insert_preprocessing_script_for_user(new_script)

        return "Script uploaded and encrypted successfully!"
    else:
        return "All fields are required!"


# Historical Financial News Scraper

from sector_finder import get_stock_company_name
@app.route('/finnews_sentiment', methods=['GET', 'POST'])
def finnews_fetcher():
    if user.User.check_logged_in():

        if request.method == 'POST':
            
            # use stock symbol to get company name and append company name to required_keywords list
            stock_symbol = request.form['stock_symbol'] if request.form['stock_symbol'] else None
            # split required kew list by comma
            date_requirement = request.form['date_selector'] if request.form['date_selector'] else None
            return redirect(url_for('finnews_results', date_requirement=date_requirement, stock_symbol=stock_symbol))
        return render_template('finnews_sentiment_fetcher.html')
    return redirect(url_for('home'))

@app.route('/finnews_results')
def finnews_results():
    if user.User.check_logged_in():

        user_id = user.User.get_id()
        import ast
        from MachineLearningModels import manual_alg_requisition_script

        # Initialize variables
        headlines = []
        article_texts = []
        urls = []
        stock_symbol = request.args.get('stock_symbol') if request.args.get('stock_symbol') else []
        date_requirement = request.args.get('date_requirement')
        date_object = datetime.strptime(date_requirement, '%Y-%m-%d').date()
        
        # Initial search to get the first batch of links
        response_text = scraper.search(date_object,stock_symbol,user_id)
        response_json = json.loads(response_text)
        articles = response_json.get("news", [])
        if not response_text:
            return render_template('finnews_results.html', articles=[])
        for article in articles:
            headline = article.get("headline", "No headline available")
            summary = article.get("summary", "No summary available")
            url = article.get("url", "No url available")
            headlines.append(headline)
            article_texts.append(summary)
            urls.append(url)
        sa_neu, sa_pos, sa_neg = manual_alg_requisition_script.process_phrase_for_sentiment(article_texts)
        sa_neu, sa_pos, sa_neg = Selenium.selenium_file.normalize_and_percentage(sa_neu, sa_pos, sa_neg)
        
        headline_url_pairs = zip(headlines, urls)
        date_format = datetime.strptime(date_requirement,"%Y-%m-%d")
        new_date_format = date_format.strftime("%B %d %Y")
        # Process links and scrape articles
        return render_template('finnews_results.html',stock_symbol=stock_symbol,new_date_format=new_date_format, 
                            headline_url_pairs=headline_url_pairs, sa_neu=sa_neu, sa_pos=sa_pos, sa_neg=sa_neg)
    return redirect(url_for('home'))
    
@app.route('/political_sentiment', methods=['GET', 'POST'])
def political_fetcher():
    if user.User.check_logged_in():

        if request.method == 'POST':
            
            # use stock symbol to get company name and append company name to required_keywords list
            # split required kew list by comma
            date_requirement = request.form['date_selector'] if request.form['date_selector'] else None
            return redirect(url_for('political_results', date_requirement=date_requirement))
        return render_template('political_sentiment_fetcher.html')
    return redirect(url_for('home'))

@app.route('/political_results')
def political_results():
    if user.User.check_logged_in():
        user_id = user.User.get_id()
        import ast
        from Selenium import selenium_file
        from MachineLearningModels import manual_alg_requisition_script

        # Initialize variables
        hyperlinks = []
        
        
        date_requirement = request.args.get('date_requirement')
        date_object = datetime.strptime(date_requirement, '%Y-%m-%d').date()
        
        # Initial search to get the first batch of links
        selenium_return = selenium_file.get_historical_political_sentiment_scores(date_object)
        date_format = datetime.strptime(date_requirement,"%Y-%m-%d")
        new_date_format = date_format.strftime("%B %d %Y")
        articles = selenium_return[1]
        new_date_format = new_date_format
        pol_neu = selenium_return[0][0]
        pol_pos = selenium_return[0][1]
        pol_neg = selenium_return[0][2]
        pol_neu, pol_pos, pol_neg = Selenium.selenium_file.normalize_and_percentage(pol_neu, pol_pos, pol_neg)
        return render_template('political_results.html', articles=articles, new_date_format=new_date_format,
                            pol_neu = pol_neu,pol_pos = pol_pos,pol_neg = pol_neg)
    return redirect(url_for('home'))

@app.route('/display_profile', methods=['GET'])
def show_profile():
    return render_template('profile.html')


if __name__ == "__main__":
    
    app.run(debug=False)
    
    
    
   
    
