from database import preprocessing_scripts_DAOIMPL, dataset_DAOIMPL, model_metrics_history_DAOIMPL
from Models import dataset
from datetime import datetime, date
import pickle
import tempfile
import subprocess
import os, logging


class Preprocessing_Script:
    
    
    def __init__(self, script_name, script_description, script_data, upload_date, user_id, preprocessed_data = None):
        self.script_name = script_name
        self.script_description = script_description
        self.script_data = script_data
        self.upload_date = upload_date
        self.user_id = user_id
        self.preprocessed_data = preprocessed_data

    def execute_preprocessing_and_save(script_content, existing_preprocessed_data, model_name, user_id):
      
        
        # Retrieve the preprocessing script from the database
        
        if not script_content:
            raise ValueError(f"No preprocessing script found for model: {model_name}")
        
        # Prepare dictionaries for executing the script
        globals_dict = globals()
        locals_dict = {}

        try:
            # Execute the preprocessing script
            exec(script_content, globals_dict, locals_dict)
        except Exception as e:
            raise RuntimeError(f"Error executing preprocessing script: {e}")

        # Retrieve the preprocessed data from local variables
        X_train = locals_dict.get('X_train')
        X_test = locals_dict.get('X_test')
        y_train = locals_dict.get('y_train')
        y_test = locals_dict.get('y_test')

        if X_train is None or y_train is None:
            raise ValueError("The preprocessing script did not produce X_train or y_train.")

        # Serialize the preprocessed data
        preprocessed_data = {
            'X_train': X_train,
            'X_test': X_test,
            'y_train': y_train,
            'y_test': y_test
        }
        preprocessed_data_binary = pickle.dumps(preprocessed_data)

        # Update the preprocessed data in the database
        try:
            if existing_preprocessed_data:
                # Update existing record
                preprocessing_scripts_DAOIMPL.update_preprocessed_data_for_user(model_name, preprocessed_data_binary)
                print(f"Preprocessed data for {model_name} updated successfully.")
            else:
                # Insert new record
                preprocessing_scripts_DAOIMPL.insert_preprocessing_script_for_user(model_name, script_content, preprocessed_data_binary)
                print(f"Preprocessed data for {model_name} saved successfully.")
        except Exception as e:
            print(f"Error saving preprocessed data: {e}")
            
            
    def retrainer_preprocessor(preprocessing_script_id, project_root, dataset_id, user_id, model_id, closed_transactions, model_name):
        #get preprocess script and convert from binary Save to temp file location.
        preprocess_script_binary = preprocessing_scripts_DAOIMPL.get_preprocessed_script_by_id(preprocessing_script_id)
        
        # De pickle to text
        preprocess_script = pickle.loads(preprocess_script_binary)

        # Ensure the content is in text format
        if isinstance(preprocess_script, bytes):
            preprocess_script = preprocess_script.decode('utf-8')  # Convert binary to text if necessary

        # Write the script content to a temporary Python file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode='w') as preprocess_writer:
            preprocess_writer.write(preprocess_script)
            tempfile_path1 = preprocess_writer.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode='w') as preprocess_ouptut_writer:
            tempfile_path2 = preprocess_ouptut_writer.name
            
            
        
        # Path where the preprocessed data will be saved by the script
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{project_root}:{env.get('PYTHONPATH', '')}"
        # Run preprocessing subprocess to output the preprocessed data
        result = subprocess.run(['/home/ubuntu/miniconda3/envs/tf-env/bin/python3.9', 
                                 tempfile_path1, 
                                 str(dataset_id), 
                                 str(user_id), tempfile_path2,str(preprocessing_script_id),model_name], 
                                capture_output=True,
                                text=True,
                                env=env  # Pass the modified environmen
                            )
        try:
            with open(tempfile_path2, 'rb') as bin_reader:
                loaded_data = pickle.load(bin_reader)
                
           
            # Deserialize the pickle output
            
        
        # Access individual components dynamically
            preprocessing_object = loaded_data.get("preprocessing_object")
            dataset_object = loaded_data.get("dataset")
            
            
    
            ppdata = pickle.dumps(preprocessing_object)
            preprocessing_scripts_DAOIMPL.update_preprocessed_data_for_user(preprocessing_script_id, ppdata)
            logging.info("Saved preprocessed data successfully.")
        
        #get most recent model_metrics_history
            mr_mmh = model_metrics_history_DAOIMPL.get_most_recent_mmh_for_model(model_id)
            month = int(mr_mmh[0])
            day = int(mr_mmh[1])
            today = date.today()
            td_month = today.month
            td_day = today.day
            if not closed_transactions:
                if month == td_month and day == td_day:
                    preprocess_writer.close()
                    preprocess_ouptut_writer.close()
                    return
            
            # Save finalized dataset
            final_df_bin = pickle.dumps(dataset_object)
            dsobject = dataset_DAOIMPL.get_dataset_object_by_id(dataset_id)
            new_dataset = dataset.Dataset(dsobject[1], dsobject[2], final_df_bin, datetime.now(), user_id)
            dataset_DAOIMPL.update_dataset(new_dataset, dataset_id)
            logging.info("Finalized dataset saved successfully.")
        except Exception as e:
            logging.error(f"Subprocess error (if any): Exception error due to {e}")
            
        preprocess_writer.close()
        preprocess_ouptut_writer.close()
    
    def retrainer_preprocessor_for_recommender(preprocessing_script_id, project_root, dataset_id, user_id, model_name):
        #get preprocess script and convert from binary Save to temp file location.
        preprocess_script_binary = preprocessing_scripts_DAOIMPL.get_preprocessed_script_by_id(preprocessing_script_id)
        
        # De pickle to text
        preprocess_script = pickle.loads(preprocess_script_binary)

        # Ensure the content is in text format
        if isinstance(preprocess_script, bytes):
            preprocess_script = preprocess_script.decode('utf-8')  # Convert binary to text if necessary

         # Write the script content to a temporary Python file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode='w') as preprocess_writer:
            preprocess_writer.write(preprocess_script)
            tempfile_path1 = preprocess_writer.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode='w') as preprocess_ouptut_writer:
            tempfile_path2 = preprocess_ouptut_writer.name
            
        
        # Path where the preprocessed data will be saved by the script
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{project_root}:{env.get('PYTHONPATH', '')}"
        # Run preprocessing subprocess to output the preprocessed data
        result = subprocess.run(['/home/ubuntu/miniconda3/envs/tf-env/bin/python3.9', 
                                 tempfile_path1, 
                                 str(dataset_id), 
                                 str(user_id), model_name,str(preprocessing_script_id)], 
                                capture_output=True,
                                text=True,
                                env=env  # Pass the modified environmen
                            )
        preprocess_writer.close()
        return result