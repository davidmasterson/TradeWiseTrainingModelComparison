from database import training_scripts_DAOIMPL, models_DAOIMPL, model_metrics_history_DAOIMPL, metrics_DAOIMPL
from Models import model, model_metrics_history, metric
from datetime import datetime
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import tempfile, subprocess
import os
import json, pickle, logging, pandas as pd


class TrainingScript:
    
    def __init__(self, model_type, script_name, script_description, script_data, created_at, user_id ):
        self.model_type = model_type
        self.script_name = script_name
        self.script_description = script_description
        self.script_data = script_data
        self.created_at = created_at
        self.user_id = user_id
        
        
        
    
    def model_trainer(training_script_id,preprocessing_script_id, model_id, user_id, model_name, project_root):
        training_script = training_scripts_DAOIMPL.get_training_script_data_by_id(training_script_id)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as training_writer:
            training_writer.write(training_script)
            tempfile_path3 = training_writer.name
            
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{project_root}:{env.get('PYTHONPATH', '')}"
        result = subprocess.run(['/home/ubuntu/miniconda3/envs/tf-env/bin/python3', 
                                  tempfile_path3,
                                  str(preprocessing_script_id),str(model_id),
                        str(user_id), model_name],
                                 capture_output=True,
                                 text=True,
                                 env=env)
        
        training_writer.close()
        
        # Check if the script ran successfully
        if result.returncode == 0:
            # Parse the JSON output
            output = json.loads(result.stdout)
            # Deserialize the model_binary
            model_binary = pickle.loads(bytes.fromhex(output['model_binary']))

            try:
                # Retrieve predictions
                y_pred = output['y_pred']
                y_test = output['y_test']
                columns = output['columns']    
            except Exception as e:
                print(f"Error deserializing output: {e}")
            try:
                 # Retrieve predictions
                y_pred = output['y_pred']
                y_test = output['y_test']
            except:
                pass
                
        else:
            print(f"Training script failed: {result.stderr}")
        
        
        
        # Check if model exists and update/insert accordingly
        model_exists = models_DAOIMPL.get_model_from_db_by_model_name_and_user_id(model_name, user_id)
        if model_exists:
            new_model = model.Model(model_exists[1], model_exists[2], model_binary, user_id, selected=1)
            model_id = models_DAOIMPL.update_model_for_user(new_model, int(model_exists[0]))
            logging.info(f"Updated existing model in the database with model_id: {model_id}")
        else:
            model_description = model_name
            new_model = model.Model(
                model_name,
                model_description,
                model_binary,
                user_id,
                selected=1
            )
            model_id = models_DAOIMPL.insert_model_into_models_for_user(new_model)
            logging.info(f"Inserted new model into the database with model_id: {model_id}")

        if not isinstance(model_id, int):
            raise ValueError("Invalid model_id returned from database function.")

        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')

        # Feature importance and top features
        this_model = pickle.loads(model_binary)
        try:
            feature_importances = this_model.feature_importances_
            top_features_df = pd.DataFrame({
                'Feature': columns,  # Use indices as feature identifiers
                'Importance': feature_importances
            }).sort_values(by='Importance', ascending=False)
            top_features_json = top_features_df.head(5).to_json(orient='records')

             # Insert metrics into model_metrics_history table
            new_history = model_metrics_history.Model_Metrics_History(
                model_id, accuracy, precision, recall, f1, datetime.now(),top_features_json
            )
            metrics_saved = model_metrics_history_DAOIMPL.insert_metrics_history(new_history)

            if metrics_saved:
                logging.info("Metrics saved successfully.")
            else:
                logging.error("Failed to save metrics in the database.")
        except:
           
            logging.info(f"Metrics - Accuracy: {accuracy}, Precision: {precision}, Recall: {recall}, F1-Score: {f1}")

            # Insert metrics into model_metrics_history table
            new_history = model_metrics_history.Model_Metrics_History(
                model_id, accuracy, precision, recall, f1, datetime.now(), '{}'
            )
            metrics_saved = model_metrics_history_DAOIMPL.insert_metrics_history(new_history)

            if metrics_saved:
                logging.info("Metrics saved successfully.")
            else:
                logging.error("Failed to save metrics in the database.")


        try:
            new_metric = metric.calculate_daily_metrics_values(user_id)
            metrics_DAOIMPL.insert_metric(new_metric)
            logging.info(f'Model {model_name} has been trained successfully.')
        except Exception as e:
            logging.error(f'Unable to insert new metric for model {model_name} due to {e}')
        
            