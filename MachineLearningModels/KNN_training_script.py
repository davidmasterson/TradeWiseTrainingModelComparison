# knn_training.py
import sys
import pickle
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from database import models_DAOIMPL, model_metrics_history_DAOIMPL, preprocessing_scripts_DAOIMPL
from Models import model, model_metrics_history
from datetime import datetime
import logging
import pandas as pd
import json


# Train and evaluate KNN model
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
        
        
        # Initialize and train KNN model
        knn_model = KNeighborsClassifier(n_neighbors=5)
        knn_model.fit(X_train, y_train)
        logging.info("KNN model training complete")

        # Predict on test data
        y_pred = knn_model.predict(X_test)

        model_binary = pickle.dumps(knn_model)
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
