from flask import Flask, render_template, request, jsonify, Response, session, redirect, url_for

from Hypothetical_Predictor import CSV_Writer, predict_with_pre_trained_model, stock_data_fetcher
import alpaca_request_methods
# import threading
import model_trainer_predictor_methods
from flask_socketio import SocketIO
# from asyncio import sleep
import os
import Hypothetical_Predictor
# import Future_Predictor
import subprocess
from database import metrics_DAOIMPL, manual_metrics_DAOIMPL, user_DAOIMPL, transactions_DAOIMPL
from Models import plotters, metric, manual_metrics, user
import bcrypt

app = Flask(__name__)
socketio = SocketIO(app)

app.secret_key = os.getenv('SECRET')

# Global variables to track progress and store predictions
alpaca_request_methods.set_socketio_instance(socketio)
predictions = []
model_trainer_predictor_methods.set_socketio_instance(socketio)


# New homepage with logo and buttons
@app.route('/')
def home():
    # If the user is logged in, redirect to the dashboard
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return render_template('home.html')  # Renders new homepage with Sign In and Sign Up buttons


@app.route('/index')
def index():
    # This will be the landing page after login (previously your home page)
    if 'logged_in' in session:
        return render_template('index.html')
    return redirect(url_for('home'))


@app.route('/create_rf_model', methods=['POST'])
def create_rf_model():
    global sio
    model_trainer_predictor_methods.model_trainer()
    percent = 100
    socketio.emit('update progress', {'percent': percent, 'type': 'model'})
    status = 'DONE'
    return render_template('index.html', status=status)


@app.route('/predict', methods=['POST'])
def predict():
    probs = model_trainer_predictor_methods.stock_predictor_using_pretrained_model()
    return render_template('stock_predictions.html', probs=probs)


@app.route('/process_symbols', methods=['POST']) 
def process_symbols():
    symbols = request.form.getlist('symbols[]')
    CSV_Writer.CSV_Writer.write_temporary_csv(symbols)
    stock_data_fetcher.fetch_stock_data()
    subprocess.run(['python', 'Hypothetical_Predictor/pre_processing.py'])
    probs = Hypothetical_Predictor.predict_with_pre_trained_model.stock_predictor_using_pretrained_model()
    return render_template('stock_predictions.html', probs=probs)


@app.route('/progress', methods=["GET"])
async def progress():
    return Response(status=204)


@app.route('/dashboard')
def dashboard():
    # User must be logged in to access the dashboard
    if 'logged_in' in session:
        return render_template('index.html')
    return redirect(url_for('home'))  # Redirect to homepage if not logged in


@app.route('/metrics_plots', methods=['GET'])
def plot_metrics():
    metric.Metric.plot_model_metrics()
    manual_metrics.Manual_metrics.plot_manual_metrics()
    return render_template('metrics_plots.html')


@app.route('/user_profile', methods=['GET'])
def user_profile():
    if 'logged_in' in session:
        last_5 = transactions_DAOIMPL.get_project_training_most_recent_5_transactions()
        user = user_DAOIMPL.get_user_by_username(session['user_id'])[0]
        return render_template('user_profile_page.html', last_5=last_5, user=user)
    return redirect(url_for('home'))  # Redirect to homepage if not logged in


# New login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data and validate
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Fetch user from the database (pseudo-code, adjust according to your setup)
        user_data = user_DAOIMPL.get_user_by_username(username)

        
        if user_data[0] is not None:
            user_data = user_data[0]
            if bcrypt.checkpw(password.encode('utf-8'), user_data['password'].encode('utf-8')):
                session['logged_in'] = True
                session['user_id'] = user_data['user']
                return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route('/transactions', methods=['GET'])
def transactions():
    transactions = transactions_DAOIMPL.get_project_training_transactions()
    return render_template('transactions.html', transactions=transactions)

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
        min_investment = float(request.form['min_investment'])
        max_investment = float(request.form['max_investment'])
        min_price = float(request.form['min_price'])
        max_price = float(request.form['max_price'])
        risk_tolerance = request.form['risk_tolerance']
        password = hash_password(password)

        new_user = user.User(first_name, last_name, username, password, email, min_investment, max_investment, min_price, max_price, risk_tolerance)
        user_DAOIMPL.insert_user(new_user)

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
    session.pop('logged_in', None)
    return redirect(url_for('home'))  # Redirect to homepage after logout


# WEBHOOKS
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print(f"Received webhook: {data}")

    if data['event'] == 'fill':
        # Handle filled orders here
        print(f"Order {data['order']['id']} filled for {data['order']['filled_qty']} shares")
    
    return jsonify({'status': 'received'}), 200

if __name__ == '__main__':
    socketio.run(app, debug=False)
