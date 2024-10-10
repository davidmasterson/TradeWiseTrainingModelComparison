import pickle
from database import models_DAOIMPL
class Model:
    
    def __init__(self, model_name, model_data, user_id):
        self.model_name = model_name
        self.model_data = model_data
        self.user_id = user_id
        
        

    @staticmethod
    def get_selected_models(user_id):
        # Retrieve the model data from the database
        model_data = models_DAOIMPL.get_comparison_trained_models_for_user(user_id)
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
            