import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pickle
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from database import preprocessing_scripts_DAOIMPL, model_metrics_history_DAOIMPL, models_DAOIMPL
from Models import model_metrics_history, model
from datetime import datetime
import logging
import json

def train_model(ppscript_id):
    from sklearn.ensemble import RandomForestClassifier
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
        # Serialize the model for storage
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train)
        

        # Predictions and metrics
        y_pred = rf_model.predict(X_test)
       

        model_binary = pickle.dumps(rf_model)
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
       
        raise

# Main execution block
if __name__ == '__main__':
    ppscript_id = int(sys.argv[1])
    train_model(ppscript_id)
