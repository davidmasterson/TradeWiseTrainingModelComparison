
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pickle
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.ensemble import RandomForestClassifier
from database import model_metrics_history_DAOIMPL, models_DAOIMPL, preprocessing_scripts_DAOIMPL
from Models import model, model_metrics_history
from datetime import datetime
import logging
import pandas as pd
import json

logging.basicConfig(
    filename='/home/ubuntu/TradeWiseTrainingModelComparison/app_debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def train_model(ppscript_id):
    """
    Train a Random Forest model using preprocessed data and return the trained model binary and predictions.
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
        # Extract preprocessed data
        X_train = preprocessed_data['X_train']
        X_test = preprocessed_data['X_test']
        y_train = preprocessed_data['y_train']
        y_test = preprocessed_data['y_test']
        columns = preprocessed_data['columns']

        # Train the Random Forest model
        logging.info("Initializing Random Forest model for training.")
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train)
        logging.info("Random Forest model training complete.")

        # Make predictions
        y_pred = rf_model.predict(X_test)

        # Serialize the model
        model_binary = pickle.dumps(rf_model)
        
        try:
            
            output = {
                'model_binary': pickle.dumps(model_binary).hex(),  #Serialize the model as a hex string
                'y_pred': y_pred.tolist(),  
                'y_test': y_test.tolist(),
                'columns': columns
                 
            }
            # Print serialized JSON to stdout
            print(json.dumps(output))
        except Exception as e:
            error_message = {"error": f"Failed to serialize output: {str(e)}"}
            print(json.dumps(error_message))
            sys.exit(1)  # Non-zero exit code to indicate failure
        
        
    except Exception as e:
        logging.error(f"Error during model saving or metric calculation: {e}")
        return



if __name__ == '__main__':
    ppscript_id = int(sys.argv[1])
    train_model(ppscript_id)