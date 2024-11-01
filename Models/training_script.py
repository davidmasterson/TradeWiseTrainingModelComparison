from database import training_scripts_DAOIMPL
import tempfile, subprocess
import os


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
        result2 = subprocess.run(['/home/ubuntu/miniconda3/envs/tf-env/bin/python3', 
                                  '/home/ubuntu/TradeWiseTrainingModelComparison/MachineLearningModels/RandomForestModel_training_script.py',
                                  str(preprocessing_script_id),str(model_id),
                        str(user_id), model_name],
                                 capture_output=True,
                                 text=True,
                                 env=env)
        training_writer.close()