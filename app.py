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


app = Flask(__name__)
socketio = SocketIO(app)

app.secret_key = os.getenv('SECRET')

# Global variables to track progress and store predictions
# Set the SocketIO instance in the alpaca_request_methods
alpaca_request_methods.set_socketio_instance(socketio)
predictions = []
model_trainer_predictor_methods.set_socketio_instance(socketio)


@app.route('/')
def index():
    
    return render_template('index.html')

@app.route('/create_rf_model', methods=['POST'])
def create_rf_model():
    global sio
    # Run the model trainer function directly
    model_trainer_predictor_methods.model_trainer()
    # Emit progress update (this should be done within the model_trainer if real-time updates are needed)
    percent = 100
    socketio.emit('update progress', {'percent': percent, 'type': 'model'})
    # Render the template after the model training is complete
    status = 'DONE'
    return render_template('index.html', status=status)


@app.route('/predict', methods=['POST'])
def predict():
    probs = model_trainer_predictor_methods.stock_predictor_using_pretrained_model()
    return render_template('stock_predictions.html', probs=probs)
    
        


@app.route('/process_symbols', methods=['POST']) 
def process_symbols():
    symbols = request.form.getlist('symbols[]')  # Get the list of symbols
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
    return render_template('dashboard.html')


    


if __name__ == '__main__':
    socketio.run(app, debug=False)
