import sys
from flask import Flask, render_template, request, jsonify, Response, session, redirect, url_for, flash
import logging
from Hypothetical_Predictor import CSV_Writer, predict_with_pre_trained_model, stock_data_fetcher
import alpaca_request_methods
# import threading
import model_trainer_predictor_methods
# from asyncio import sleep
import os
import Hypothetical_Predictor
# import Future_Predictor
import subprocess
from database import metrics_DAOIMPL, manual_metrics_DAOIMPL, user_DAOIMPL, transactions_DAOIMPL, user_preferences_DAOIMPL
from Models import plotters, metric, manual_metrics, user, user_preferences
import bcrypt
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

# New homepage with logo and buttons
@app.route('/', methods=['GET'])
def home():
    # If the user is logged in, redirect to the dashboard
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
    return render_template('home.html')  # Renders new homepage with Sign In and Sign Up buttons


@app.route('/index', methods=['GET'])
def index():
    # This will be the landing page after login (previously your home page)
    if session.get('logged_in'):
        return render_template('index.html')
    return redirect(url_for('home'))


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
    # User must be logged in to access the dashboard
    if session.get('logged_in'):
        return render_template('index.html')
    return redirect(url_for('home'))  # Redirect to homepage if not logged in


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
        return render_template('user_profile_page.html', last_5=last_5, user=user, equity=equity, cash=cash, pref=pref)
    return redirect(url_for('home'))  # Redirect to homepage if not logged in


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data and validate
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Fetch user from the database
        user_data = user_DAOIMPL.get_user_by_username(username)[0]
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

@app.route('/transactions', methods=['GET'])
def transactions():
    if session.get('logged_in'):
        user_id = session.get('user_id')
        transactions = transactions_DAOIMPL.get_project_training_transactions_for_user(user_id)
        return render_template('transactions.html', transactions=transactions)
    return redirect(url_for('home'))

# New sign-up route (already included in your existing routes)
@app.route('/submit_signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get the form data
        first_name = request.form.get('first')
        last_name = request.form.get('last')
        username = request.form.get('user')
        password = request.form.get('password')
        email = request.form['email']
        alpaca_key = request.form['alpaca_key']
        alpaca_secret = request.form['alpaca_secret_key']
        min_investment = float(request.form['min_investment'])
        max_investment = float(request.form['max_investment'])
        min_price_per_share = float(request.form['min_price'])
        max_price_per_share = float(request.form['max_price'])
        risk_tolerance = request.form['risk_tolerance']
        password = hash_password(password)
        
        #check for existing user
        user_found = len(user_DAOIMPL.get_user_by_username(username)) > 0
        if user_found:
            error_message = 'Please choose a different username.'
            return render_template('signup.html', error_message=error_message)

        new_user = user.User(first_name, last_name, username, password, email, alpaca_key, alpaca_secret)
        confirm = user_DAOIMPL.insert_user(new_user)
        if confirm:
            user_found = user_DAOIMPL.get_user_by_username(username)[0]
            new_preferences = user_preferences.UserPreferences(min_investment, max_investment, min_price_per_share, max_price_per_share, user_found['id'],  risk_tolerance)
            user_preferences_DAOIMPL.insert_user_preferance(new_preferences)
        

        return redirect(url_for('login'))  # Redirect to login page after successful sign-up

    return render_template('signup.html')


# Password hashing function
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password


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








def run_alpaca_websocket(username):
    """ Thread target function to handle websocket connection """

    async def websocket_task():
        try:
            logging.info("Attempting to connect to Alpaca WebSocket...")
            conn = alpaca_request_methods.get_alpaca_stream_connection(username)
            if conn is None:
                logging.error("Failed to connect to Alpaca WebSocket. Retrying...")
                return

            transactions = transactions_DAOIMPL.get_open_transactions_for_user(7)
            transactions_dict = {}
            for transaction in transactions:
                transactions_dict[transaction[1]] = {
                    'id': transaction[0],
                    'symbol': transaction[1],
                    'client_order_id': f'{transaction[6]}~sell',
                    'take_profit': float(transaction[14]),
                    'stop_price': float(transaction[15])
                }

            # Define your quote handler
            async def on_quote(data):
                transaction = transactions_dict.get(data.symbol, None)
                if transaction:
                    # Check for take profit or stop out
                    if data.askprice >= transaction['take_profit']:
                        logging.info(f"Take Profit hit for {data.symbol} at {data.askprice}.")
                        order_methods.place_sell_order(transaction['symbol'], int(transaction['quantity']), float(data.askprice), int(transaction['id']), username)
                    elif data.bidprice <= transaction['stop_price']:
                        logging.info(f"Stop Out hit for {data.symbol} at {data.bidprice}.")
                        order_methods.place_sell_order(transaction['symbol'], int(transaction['quantity']), float(data.bidprice), int(transaction['id']), username)

            logging.info("Subscribing to trade updates...")
            conn.subscribe_trade_updates(alpaca_request_methods.handle_trade_updates)
            logging.info(f"Successfully subscribed to trade updates for user {username}")

            # Subscribe to quote updates for all symbols
            symbols = list(transactions_dict.keys())
            for sym in symbols:
                logging.info(f"Subscribing to quotes for symbol {sym}")
                conn.subscribe_quotes(on_quote, sym)
                logging.info(f'Successfully subscribed to quotes for symbol {sym}')

           # We use this to keep the connection alive and process received messages
            while True:
                await asyncio.sleep(1)

        except Exception as e:
            logging.error(f"WebSocket connection error: {e}. Reconnecting...")
    

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Add websocket_task to the event loop if running
    if loop.is_running():
        loop.create_task(websocket_task())  # Schedule it as a new task
    else:
        # Otherwise, run the event loop and task
        loop.run_until_complete(websocket_task())

@app.route('/start_websocket/<username>')
def start_websocket_route(username):
    # Trigger the websocket connection without creating a new event loop
    thread = threading.Thread(target=run_alpaca_websocket, args=(username,))
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









######DEBUG FUNCTIONS#################
def log_event_loop_status(prefix=""):
    loop = asyncio.get_event_loop()
    logging.info(f"{prefix} Event loop running: {loop.is_running()}, closed: {loop.is_closed()}")


if __name__ == '__main__':
    
    app.run(debug=False)
    
