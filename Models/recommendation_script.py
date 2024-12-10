from database import recommendation_scripts_DAOIMPL, models_DAOIMPL
import pickle
import tempfile
import os
import subprocess
import logging

class RecommendationScript:
    
    def __init__(self, script_name, script_description, script, user_id, updated):
        self.script_name = script_name
        self.script_description = script_description
        self.script = script
        self.user_id = user_id
        self.updated = updated
        
        
    def retrainer_for_recommender(recommendation_script_id, project_root, user_id, dataset_id):
        #get preprocess script and convert from binary Save to temp file location.
        recommender_script_list = recommendation_scripts_DAOIMPL.get_recommendation_script_by_script_id(recommendation_script_id)
        recommender_script_bin = recommender_script_list[0][3]
        
        # De pickle to text
        recommendation_script = pickle.loads(recommender_script_bin)

        # Ensure the content is in text format
        if isinstance(recommendation_script, bytes):
            recommendation_script = recommendation_script.decode('utf-8')  # Convert binary to text if necessary

        # Write the script content to a temporary Python file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode='w') as recommendations_writer:
            recommendations_writer.write(recommendation_script)
            tempfile_path1 = recommendations_writer.name
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode='w') as recommendations_writer2:
            recommendations_writer2.write(recommendation_script)
            tempfile_path2 = recommendations_writer2.name
            
        
        # Path where the preprocessed data will be saved by the script
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{project_root}:{env.get('PYTHONPATH', '')}"
        # Run preprocessing subprocess to output the preprocessed data
        result = subprocess.run(['/home/ubuntu/miniconda3/envs/tf-env/bin/python3.9', 
                                tempfile_path1,
                                str(user_id), tempfile_path2, dataset_id], 
                                stdout=subprocess.PIPE,  # Capture standard output
                                stderr=subprocess.PIPE,  # Capture standard error
                                text=False,  # Prevent automatic decoding
                                env=env ) # Pass the modified environmen
        
        if result.returncode != 0:
            logging.error(f"Subprocess failed with return code {result.returncode} and error: {result.stderr.decode('utf-8', errors='replace')}")
            raise RuntimeError("Subprocess execution failed.")
                            
        # Read the contents of the file and pass them to pickle.loads
        with open(tempfile_path2, 'rb') as bin_reader:
            loaded_data = pickle.loads(bin_reader.read())  # Correct usage
        
        recommendations_writer.close()
        recommendations_writer2.close()
        return loaded_data