
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pickle
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from database import model_metrics_history_DAOIMPL, models_DAOIMPL, preprocessing_scripts_DAOIMPL
from Models import model, model_metrics_history
from datetime import datetime
import logging
import pandas as pd

logging.basicConfig(
    filename='/home/ubuntu/TradeWiseTrainingModelComparison/app_debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def train_model(ppscript_id, model_id, user_id, model_name):
    from flask import flash
    # Deserialize the temp file and convert strings to ints
    try:
        ppdata_bin = preprocessing_scripts_DAOIMPL.get_preprocessed_data_by_preprocessing_script_id(ppscript_id)
        preprocessed_data = pickle.loads(ppdata_bin)
    except Exception as e:
        return
    
    logging.info('Passed the decoding of preprocessed data')
    try:
        X_train = preprocessed_data['X_train']
        y_train = preprocessed_data['y_train']
        X_test = preprocessed_data['X_test']
        y_test = preprocessed_data['y_test']
        scaler = preprocessed_data['scaler']
        from sklearn.ensemble import RandomForestClassifier  # Importing inside the function as specified
        logging.info("Initializing Random Forest model for training.")
        
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train)
        
        logging.info("Random Forest model training complete.")
        # Serialize the model
        model_binary = pickle.dumps(rf_model)
        
        model_exists = models_DAOIMPL.get_model_from_db_by_model_name_and_user_id(model_name, user_id)
        if model_exists:
            new_model = model.Model(model_exists[1], model_exists[2], model_binary, user_id, selected=1)
            model_id = models_DAOIMPL.update_model_for_user(new_model, int(model_exists[0]))
            logging.info(f"Updated existing model in the database with model_id: {model_id}")
        else:
            new_model = model.Model(model_name, "Random Forest for 12-day profit/loss prediction.", model_binary, user_id, selected=1)
            model_id = models_DAOIMPL.insert_model_into_models_for_user(new_model)
            logging.info(f"Inserted new model into the database with model_id: {model_id}")
        # Check if model_id is valid
        if not isinstance(model_id, int):
            logging.error("Invalid model_id returned. Aborting metric saving.")
            raise ValueError("Invalid model_id returned from database function.")
        # Evaluate and save metrics
        y_pred = rf_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')
        # Feature importance (specific to RandomForest)
        feature_importances = rf_model.feature_importances_
        top_features_df = pd.DataFrame({
            'Feature': preprocessed_data['columns'],
            'Importance': feature_importances
        }).sort_values(by='Importance', ascending=False)
        top_features_json = top_features_df.head(5).to_json(orient='records')
        logging.info(f"Metrics - Accuracy: {accuracy}, Precision: {precision}, Recall: {recall}, F1-Score: {f1}")
        
        # Insert metrics into model_metrics_history table
        new_history = model_metrics_history.Model_Metrics_History(
            model_id, accuracy, precision, recall, f1, top_features_json, datetime.now()
        )
        metrics_saved = model_metrics_history_DAOIMPL.insert_metrics_history(new_history)
        
        if metrics_saved:
            logging.info("Metrics saved successfully.")
        else:
            logging.error("Failed to save metrics in the database.")
    except Exception as e:
        logging.error(f"Error during model saving or metric calculation: {e}")
        return


if __name__ == '__main__':
    ppscript_id = int(sys.argv[1])
    model_id = sys.argv[2]
    user_id = sys.argv[3]
    model_name = sys.argv[4]
    train_model(ppscript_id, model_id, user_id, model_name)