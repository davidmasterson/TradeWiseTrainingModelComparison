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


# Train and evaluate KNN model
def train_model(ppscript_id, model_id, user_id, model_name):
    try: 
        # Load preprocessed data
        try:
            ppdata_bin = preprocessing_scripts_DAOIMPL.get_preprocessed_data_by_preprocessing_script_id(ppscript_id)
            preprocessed_data = pickle.loads(ppdata_bin)
        except Exception as e:
            return
        
        X_train = preprocessed_data['X_train']
        X_test = preprocessed_data['X_test']
        y_train = preprocessed_data['y_train']
        y_test = preprocessed_data['y_test']

        # Initialize and train KNN model
        knn_model = KNeighborsClassifier(n_neighbors=5)
        knn_model.fit(X_train, y_train)

        # Predict on test data
        y_pred = knn_model.predict(X_test)

        # Calculate evaluation metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')

        
        metrics = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1' : f1
        }
        # Print results for confirmation
        print(f"Accuracy: {accuracy}")
        print(f"Precision: {precision}")
        print(f"Recall: {recall}")
        print(f"F1-Score: {f1}")

        model_binary = pickle.dumps(knn_model)
        db_model = models_DAOIMPL.get_model_from_db_by_model_name_and_user_id(model_name,user_id)
        if not db_model:    
            logging.error(f'Unable to continue training process because model name {model_name} for user {user_id} does not exist.')
            return
        new_model = model.Model(model_name,db_model[2],model_binary,user_id,1) 
        models_DAOIMPL.update_model_for_user(new_model,db_model[0])
        logging.info(f'Successfully updated model {model_name} for user {user_id}')
        # Insert model metrics into database
        top_features = '{}'
        logging.info(f"Metrics - Accuracy: {metrics['accuracy']}, Precision: {metrics['precision']}, Recall: {metrics['recall']}, F1-Score: {metrics['f1']}")
        
        # Insert metrics into model_metrics_history table
        new_history = model_metrics_history.Model_Metrics_History(
            model_id, metrics['accuracy'], metrics['precision'], metrics['recall'], metrics['f1'], top_features, datetime.now()
        )
        metrics_saved = model_metrics_history_DAOIMPL.insert_metrics_history(new_history)
        
        if metrics_saved:
            logging.info("Metrics saved successfully.")
        else:
            logging.error("Failed to save metrics in the database.")
    except Exception as e:
        raise

# Main execution block
if __name__ == '__main__':
    ppscript_id = int(sys.argv[1])
    model_id = sys.argv[2]
    user_id = sys.argv[3]
    model_name = sys.argv[4]
    train_model(ppscript_id, model_id, user_id, model_name)
