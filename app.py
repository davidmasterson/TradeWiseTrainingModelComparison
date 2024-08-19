from flask import Flask, render_template, request, jsonify
import alpaca_request_methods
import threading
import model_trainer_predictor_methods

app = Flask(__name__)

# Global variables to track progress and store predictions
progress = 0
predictions = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_rf_model', methods=['GET'])
def create_rf_model():
    global progress
    model_trainer_predictor_methods.model_trainer()
    return render_template('index.html')

@app.route('/predict', methods=['GET'])
def predict():
    global progress
    probs = model_trainer_predictor_methods.stock_predictor_using_pretrained_model()
    print(probs)
    return render_template('stock_predictions.html', probs=probs)

@app.route('/progress')
def get_progress():
    global progress
    return jsonify({"progress": progress})


if __name__ == '__main__':
    app.run(debug=False)
