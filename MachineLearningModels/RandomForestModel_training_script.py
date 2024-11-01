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

def train_model(ppscript_id, model_id, user_id,model_name ):
    from sklearn.ensemble import RandomForestClassifier
    try:
        ppdata_bin = preprocessing_scripts_DAOIMPL.get_preprocessed_data_by_preprocessing_script_id(ppscript_id)
        preprocessed_data = pickle.loads(ppdata_bin)
    except Exception as e:
        return
    try:
        X_train = preprocessed_data['X_train']
        y_train = preprocessed_data['y_train']
        X_test = preprocessed_data['X_test']
        y_test = preprocessed_data['y_test']
        scaler = preprocessed_data['scaler']
        # Serialize the model for storage
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train)
        
        # Convert to binary and update model in database for user
        model_binary = pickle.dumps(rf_model)
        db_model = models_DAOIMPL.get_model_from_db_by_model_name_and_user_id(model_name,user_id)
        if not db_model:    
            logging.error(f'Unable to continue training process because model name {model_name} for user {user_id} does not exist.')
            return
        new_model = model.Model(model_name,db_model[2],model_binary,user_id,1) 
        models_DAOIMPL.update_model_for_user(new_model,db_model[0])
        logging.info(f'Successfully updated model {model_name} for user {user_id}')
        


        # Predictions and metrics
        y_pred = rf_model.predict(X_test)
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, average='weighted'),
            "recall": recall_score(y_test, y_pred, average='weighted'),
            "f1": f1_score(y_test, y_pred, average='weighted')
        }
        
        # Feature importance (specific to RandomForest)
        feature_importances = rf_model.feature_importances_
        top_features_df = pd.DataFrame({
            'Feature': preprocessed_data['columns'],
            'Importance': feature_importances
        }).sort_values(by='Importance', ascending=False)
        top_features_json = top_features_df.head(5).to_json(orient='records')
        logging.info(f"Metrics - Accuracy: {metrics['accuracy']}, Precision: {metrics['precision']}, Recall: {metrics['recall']}, F1-Score: {metrics['f1']}")
        
        # Insert metrics into model_metrics_history table
        new_history = model_metrics_history.Model_Metrics_History(
            model_id, metrics['accuracy'], metrics['precision'], metrics['recall'], metrics['f1'], top_features_json, datetime.now()
        )
        metrics_saved = model_metrics_history_DAOIMPL.insert_metrics_history(new_history)
        
        if metrics_saved:
            logging.info("Metrics saved successfully.")
        else:
            logging.error("Failed to save metrics in the database.")

        
    except Exception as e:
       
        raise

if __name__ == '__main__':
    ppscript_id = int(sys.argv[1])
    model_id = sys.argv[2]
    user_id = sys.argv[3]
    model_name = sys.argv[4]
    train_model(ppscript_id, model_id, user_id, model_name)
