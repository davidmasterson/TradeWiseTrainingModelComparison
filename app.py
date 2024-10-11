import sys
from flask import Flask, render_template, request, jsonify, Response, redirect, url_for, flash
import logging
from Hypothetical_Predictor import CSV_Writer, predict_with_pre_trained_model, stock_data_fetcher
import alpaca_request_methods
# import threading
import model_trainer_predictor_methods
from Models import preprocessing_script, metric, user_preferences, model_metrics_history
# from asyncio import sleep
import os
import Hypothetical_Predictor
# import Future_Predictor
import subprocess
from database import metrics_DAOIMPL, manual_metrics_DAOIMPL,  transactions_DAOIMPL, user_preferences_DAOIMPL, preprocessing_scripts_DAOIMPL, model_metrics_history_DAOIMPL


import threading
import time
from Finder import symbol_finder
from Recommender import recommender
from Purchaser import score_based_purchaser, purchaser
import queue
import order_methods
import requests
from flask_cors import CORS
import asyncio
from datetime import datetime
import websocket
import json


app = Flask(__name__)

CORS(app, supports_credentials=True)
app.secret_key = os.getenv('SECRET')

# Global variables to track progress
progress = 0
result_queue = queue.Queue()




# Set up logging
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
    datefmt='%Y-%m-%d %H:%M:%S'
)
# Attach logging to Flask's logger and configure it to log to the console as well
app.logger.addHandler(logging.StreamHandler(sys.stdout))  # Outputs logs to console
app.logger.setLevel(logging.ERROR)  # Logs errors only

#Public Homepage
@app.route('/', methods=['GET'])
def home():
    # If the user is logged in, redirect to the dashboard
    if session.get('logged_in'):
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
from database import user_DAOIMPL
from Models import user
from flask import session

# New sign-up route (already included in your existing routes)
@app.route('/submit_signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get the form data
        first_name = request.form.get('first')
        last_name = request.form.get('last')
        user_name = request.form.get('user')
        password = request.form.get('password')
        email = request.form['email']
        alpaca_key = request.form['alpaca_key']
        alpaca_secret = request.form['alpaca_secret_key']
        password = user.User.hash_password(password)
        
        #check for existing user
        user_found = user_DAOIMPL.get_user_by_username(user_name)
        if user_found:
            error_message = 'Please choose a different user_name.'
            return render_template('signup.html', error_message=error_message)

        new_user = user.User(first_name, last_name, user_name, password, email, alpaca_key, alpaca_secret)
        user_DAOIMPL.insert_user(new_user)
        
        

        return render_template('login.html', success = 'Your account was created successfully!')  # Redirect to login page after successful sign-up

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data and validate
        username = request.form.get('username')
        password = request.form.get('password')
        # Fetch user from the database
        user_data = user_DAOIMPL.get_user_by_username(username)
        logging.info( f'this is the {user_data}')
        if user_data is not None:
            if bcrypt.checkpw(password.encode('utf-8'), user_data['password'].encode('utf-8')):
                session['logged_in'] = True
                session['user_name'] = user_data['user_name']
                session['user_id'] = user_data['id']
                logging.info(f'session is {session}')
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
    return render_template('login.html')

# ---------------------------------------------------END USER MANAGEMENT -------------------------------------------------------------------------------------
@app.route('/create_rf_model', methods=['POST'])
def create_rf_model():
    model_trainer_predictor_methods.model_trainer()
    percent = 100
    status = 'DONE'
    return render_template('index.html', status=status)


@app.route('/predict', methods=['POST'])
def predict():
    probs = model_trainer_predictor_methods.stock_predictor_using_pretrained_model()
    return render_template('stock_predictions.html', probs=probs)


@app.route('/process_symbols', methods=['POST']) 
def process_symbols():
    file_path = 'path/to/your/file.txt'

    if os.path.exists(file_path):
        print("The file exists.")
    else:
        print("The file does not exist.")
    symbols = request.form.getlist('symbols[]')
    CSV_Writer.CSV_Writer.write_temporary_csv(symbols)
    stock_data_fetcher.fetch_stock_data()
    
    subprocess.run(['python3', 'Hypothetical_Predictor/pre_processing.py'])
    probs = Hypothetical_Predictor.predict_with_pre_trained_model.stock_predictor_using_pretrained_model()
    return render_template('stock_predictions.html', probs=probs)



@app.route('/dashboard', methods=['GET'])
def dashboard():
    if session.get('logged_in'):
        user_id = session.get('user_id')
        model_metrics = model_metrics_history_DAOIMPL.get_most_recent_metric_for_user_selected_models(user_id)
        # Get the latest metric by model name
        model_metrics = model_metrics_history.Model_Metrics_History.get_most_recent_metric(model_metrics)

        historical_metrics = model_metrics_history_DAOIMPL.get_all_metrics_history_for_selected_models(user_id)
        logging.info(f"historical_metrics {historical_metrics}")
        logging.info(f'model metrics: {model_metrics}')
        if model_metrics:
            metrics_data = []
            for metric in [model_metrics]:
                top_features_dict = json.loads(metric[6])  # Load JSON into a dictionary
                sorted_features = dict(sorted(top_features_dict.items(), key=lambda item: item[1], reverse=True)[:5])  # Sort and limit to top 5
                
                metrics_data.append({
                    'model_name': metric[1],
                    'accuracy': float(metric[2]),
                    'precision': float(metric[3]),
                    'recall': float(metric[4]),
                    'f1_score': float(metric[5]),
                    'top_features': sorted_features,  # Now it contains sorted features
                    'timestamp': metric[7]
                })
            logging.info(metrics_data)
            return render_template('index.html', metrics_data=metrics_data, historical_metrics=historical_metrics)
        
        return render_template('index.html')  # If no metrics found
    return redirect(url_for('home'))



@app.route('/metrics_plots', methods=['GET'])
def plot_metrics():
    if session.get('logged_in'):
        metrics = metrics_DAOIMPL.get_metrics_by_user_id(session.get('user_id'))
        if metrics:
            metric.Metric.plot_model_metrics()
            # manual_metrics.Manual_metrics.plot_manual_metrics()
            return render_template('metrics_plots.html')
        message = 'There are not any metrics yet!'
        return render_template('metrics_plots.html', message=message)
    return redirect(url_for('home'))


@app.route('/user_profile', methods=['GET', 'POST'])
def user_profile():
    if session.get('logged_in'):
        user_id = session.get('user_id')
        last_5 = transactions_DAOIMPL.get_project_training_most_recent_5_transactions_for_user(user_id)
        user = user_DAOIMPL.get_user_by_username(session.get('user_name'))[0]
        pref = user_preferences_DAOIMPL.get_user_preferences(user_id)
        conn = alpaca_request_methods.create_alpaca_api(session.get('user_name'))
        account = conn.get_account()
        equity = float(account.equity)
        cash = float(account.cash)
        user_script_names = preprocessing_scripts_DAOIMPL.get_preprocessing_script_names_and_dates_for_user(user_id)
        if user_script_names:
            print(user_script_names)
            user_script_names = user_script_names
        return render_template('user_profile_page.html', last_5=last_5, user=user, equity=equity, cash=cash, pref=pref, user_script_names=user_script_names)
    return redirect(url_for('home'))  # Redirect to homepage if not logged in




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
    if session.get('logged_in'):
        session.clear()
        return redirect(url_for('home'))  # Redirect to homepage after logout
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










@app.route('/purchaser', methods=['GET', 'POST'])
def purchaser_page():
    if session.get('logged_in'):
        user_name = session.get('user_name')
        api = alpaca_request_methods.create_alpaca_api(user_name)
        user_account = api.get_account()
        cash = float(user_account.cash)
    
    

        if request.method == 'POST':
            # Generate recommendations and store them in the session
            orders = purchaser.generate_recommendations_task(user_name)
            session['orders'] = orders  # Store recommendations in session
            return render_template('purchaser.html', orders=orders, user_cash=cash)

        # Load recommendations from session if they exist
        orders = session.get('orders', None)
        return render_template('purchaser.html', orders=orders, user_cash=cash)
    return redirect(url_for('home'))
    

@app.route('/purchase', methods=['POST'])
def purchase_stock():
    if session.get('logged_in'):
        # Extract form data
        symbol = request.form.get('symbol')
        limit_price = float(request.form.get('limit_price'))
        qty = int(request.form.get('qty'))

        try:
            order = {
                'symbol': symbol,
                'limit_price': limit_price,
                'qty': qty,
                'side': 'buy',
                'type': 'limit',
                'tif': 'gtc'  # Good 'til canceled
            }
            # Call Alpaca's purchase method to execute the order
            order_methods.submit_limit_order(session.get('user_name'), order)
            
            # Flash a success message
            flash(f"Successfully placed an order for {qty} shares of {symbol} at ${limit_price}!", 'success')
        except Exception as e:
            # Flash an error message
            flash(f"Failed to place order for {symbol}. Error: {e}", 'danger')
        
        # Redirect back to the purchaser page
        return redirect(url_for('purchaser_page'))
    return redirect(url_for('home'))


    
    

        
       
@app.route('/progress', methods=['GET'])
def get_progress():
    global progress
    return jsonify({'progress': progress})










@app.route('/start_websocket/<username>')
def start_websocket_route(username):
    # Start the WebSocket in a separate thread to avoid blocking Flask
    thread = threading.Thread(target=alpaca_request_methods.run_alpaca_websocket, args=(username,))
    thread.start()
    return "WebSocket connection initiated"



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



######DEBUG FUNCTIONS#################
def log_event_loop_status(prefix=""):
    loop = asyncio.get_event_loop()
    logging.info(f"{prefix} Event loop running: {loop.is_running()}, closed: {loop.is_closed()}")



if __name__ == "__main__":
    app.run(debug=False)
    start_websocket_route(session.get('user_name'))

    
   
    
