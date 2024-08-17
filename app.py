from flask import Flask, render_template, request, jsonify
from alpaca_request_methods import fetch_stock_data
from LSTM_Trainer import train_lstm
import threading

app = Flask(__name__)

# Global variables to track progress and store predictions
progress = 0
predictions = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    global progress, predictions
    symbols = request.form.getlist('symbols')
    if not symbols or len(symbols) == 0:
        return jsonify({"error": "No stock symbols provided"}), 400

    try:
        data = fetch_stock_data(symbols)
        if data.empty:
            return jsonify({"error": "No data found for the provided symbols"}), 404

        progress = 0  # Reset progress
        predictions = []  # Clear previous predictions

        def run_predictions():
            global progress, predictions
            try:
                progress = 10  # Initializing

                # Fetching data
                # Simulate longer prediction process for demo
                progress = 20
                
                # Train LSTM model
                predictions = train_lstm(data, update_progress)

                progress = 100  # Mark progress as complete

            except Exception as e:
                progress = 100  # Mark progress as complete on error
                predictions = [{"error": str(e)}]

        def update_progress(step, total_steps):
            global progress
            progress = int((step / total_steps) * 100)

        # Run predictions in a separate thread to avoid blocking
        prediction_thread = threading.Thread(target=run_predictions)
        prediction_thread.start()

        return jsonify({"message": "Prediction started"}), 202

    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
