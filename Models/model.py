import pickle
from database import models_DAOIMPL
class Model:
    
    def __init__(self, model_name, model_description, model_data, user_id, selected):
        self.model_name = model_name
        self.model_description = model_description
        self.model_data = model_data
        self.user_id = user_id
        self.selected = selected
        
        
        

    @staticmethod
    def get_selected_models():
        # Retrieve the model data from the database
        model_data = models_DAOIMPL.get_comparison_trained_models()
        models = []
        if model_data:
            for model_entry in model_data:
                # Deserialize the model from BLOB
                model = pickle.loads(model_entry.model_data)
                models.append({
                    'model_name': model_entry.model_name,
                    'model': model
                })
            return models
        return None

    @staticmethod
    def get_model_metrics(models):
        models_metrics = []
        for model_entry in models:
            model = model_entry['model']
            # Assume you have a method to calculate or get metrics from a model
            model_metrics = {
                'model_name': model_entry['model_name'],
                'accuracy': model.get_accuracy(),  # Custom method on the model
                'precision': model.get_precision(),  # Example placeholder
                'recall': model.get_recall(),
                'f1_score': model.get_f1_score(),
                'top_features': model.get_top_features(),  # Assuming top features exist
                'last_trained': model.get_last_trained()  # If you store this
            }
            models_metrics.append(model_metrics)
        return models_metrics
            
            
    
    
    
    # Retrieve model from database
    def retrieve_model_from_database(model_name, user_id):
        stored_model = models_DAOIMPL.get_model_blob_from_db_by_model_name_and_user_id(model_name, user_id)
        if stored_model is None:
            raise ValueError(f'No model found for {model_name} for user {user_id}')
        model = pickle.loads(stored_model)
        return model
    
    # Train or Retrain model
    def train_retrain_model(model_name, x_train, y_train):
        model_name.fit(x_train, y_train)
        return model_name
    
    # Save updated model back to DB
    def save_updated_model_back_to_db(model, model_name, model_description, user_id):
        # serialize the model
        model_bin = pickle.dumps(model)
        updated_model = Model(model_name, model_description, model_bin, user_id, 1)
        