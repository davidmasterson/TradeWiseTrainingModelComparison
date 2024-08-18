from flask import Flask, render_template, request, jsonify
from alpaca_request_methods import fetch_stock_data
from LSTM_Trainer import train_lstm
import threading
import model_trainer_predictor_methods

app = Flask(__name__)

# Global variables to track progress and store predictions
progress = 0
predictions = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_rf_model', methods=['POST'])
def create_rf_model():
    global progress
    model_trainer_predictor_methods.model_trainer()

@app.route('/progress')
def get_progress():
    global progress
    return jsonify({"progress": progress})

@app.route('/predictions')
def get_predictions():
    global predictions
    return jsonify(predictions)

if __name__ == '__main__':
    app.run(debug=False)
