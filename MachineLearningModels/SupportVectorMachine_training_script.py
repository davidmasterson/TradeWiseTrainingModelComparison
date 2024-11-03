# svm_training.py
import sys
import pickle
from sklearn import svm
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from datetime import datetime
import joblib
from database import models_DAOIMPL, model_metrics_history_DAOIMPL, preprocessing_scripts_DAOIMPL
from Models import model, model_metrics_history
import logging

# Load preprocessed data
def load_preprocessed_data():
    with open('preprocessed_data.pkl', 'rb') as f:
        preprocessed_data = pickle.load(f)
    return preprocessed_data

# Convert predictions to binary based on a threshold
def convert_to_binary_with_tp1(predictions, tp1_values):
    return (predictions >= tp1_values).astype(int)

# Train the SVM model
def train_model(ppscript_id, model_id, user_id, model_name):
    try:
        try:
            ppdata_bin = preprocessing_scripts_DAOIMPL.get_preprocessed_data_by_preprocessing_script_id(ppscript_id)
            preprocessed_data = pickle.loads(ppdata_bin)
        except Exception as e:
            return
        # Load preprocessed data
        X_train = preprocessed_data['X_train']
        X_test = preprocessed_data['X_test']
        y_train = preprocessed_data['y_train']
        y_test = preprocessed_data['y_test']

        # Initialize and train the SVM model
        svm_model = svm.SVR()
        svm_model.fit(X_train, y_train)

        # Make predictions on the test set
        y_pred = svm_model.predict(X_test)

        # Convert to binary for classification-style evaluation
        y_pred_binary = convert_to_binary_with_tp1(y_pred, y_test)
        y_test_binary = convert_to_binary_with_tp1(y_test, y_test)

        # Evaluate the model
        accuracy = accuracy_score(y_test_binary, y_pred_binary)
        precision = precision_score(y_test_binary, y_pred_binary)
        recall = recall_score(y_test_binary, y_pred_binary)
        f1 = f1_score(y_test_binary, y_pred_binary)

        print(f"Accuracy: {accuracy}, Precision: {precision}, Recall: {recall}, F1-Score: {f1}")
        metrics = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1
        }

        model_binary = pickle.dumps(svm_model)
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

# Main execution
if __name__ == '__main__':
    ppscript_id = int(sys.argv[1])
    model_id = sys.argv[2]
    user_id = sys.argv[3]
    model_name = sys.argv[4]
    train_model(ppscript_id, model_id, user_id, model_name)
