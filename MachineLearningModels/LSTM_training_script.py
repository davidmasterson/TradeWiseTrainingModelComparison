# lstm_training.py
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tensorflow import keras
from keras.layers import LSTM, Dense, Dropout
from keras.models import Sequential
import pickle
from database import preprocessing_scripts_DAOIMPL
import logging
import json

# Load preprocessed data
def load_preprocessed_data():
    with open('preprocessed_lstm_data.pkl', 'rb') as f:
        preprocessed_data = pickle.load(f)
    return preprocessed_data

# Build LSTM model
def create_lstm_model(input_shape):
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(input_shape[1], input_shape[2])))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(units=25))
    model.add(Dense(units=1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

# Train and evaluate LSTM model
def train_model(ppscript_id):
    """
    Train a model using preprocessed data and return the trained model binary and predictions.
    """
    try:
        # Fetch preprocessed data
        ppdata_bin = preprocessing_scripts_DAOIMPL.get_preprocessed_data_by_preprocessing_script_id(ppscript_id)
        preprocessed_data = pickle.loads(ppdata_bin)
        logging.info("Preprocessed data loaded successfully.")
    except Exception as e:
        logging.error(f"Failed to load preprocessed data: {e}")
        return None, None, f"Failed to load preprocessed data: {e}"
    
    try:    
        X_train = preprocessed_data['X_train']
        X_test = preprocessed_data['X_test']
        y_train = preprocessed_data['y_train']
        y_test = preprocessed_data['y_test']
        
    

         # Train the Long Short Term Memory model
        logging.info("Initializing Long Short Term Memory model for training.")
        lstm_model = create_lstm_model(X_train.shape)
        lstm_model.fit(X_train, y_train, epochs=20, batch_size=32)

        # Get predictions
        y_pred = lstm_model.predict(X_test)
        

        # # Convert predictions for evaluation
        # y_pred_binary = (y_pred >= y_test.mean()).astype(int)
        # y_test_binary = (y_test >= y_test.mean()).astype(int)

        
        # Prepare standardized output
        model_binary = pickle.dumps(lstm_model)
        try:
            
            output = {
                'model_binary': pickle.dumps(model_binary).hex(),  #Serialize the model as a hex string
                'y_pred': y_pred.tolist(),  
                'y_test': y_test.tolist(),    
            }
            # Print serialized JSON to stdout
            print(json.dumps(output))
        except Exception as e:
            error_message = {"error": f"Failed to serialize output: {str(e)}"}
            print(json.dumps(error_message))
            sys.exit(1)  # Non-zero exit code to indicate failure
    except Exception as e:
        logging.error(f"Error during model saving or metric calculation: {e}")
        raise
    

# Main execution block
if __name__ == '__main__':
    ppscript_id = int(sys.argv[1])
    train_model(ppscript_id)