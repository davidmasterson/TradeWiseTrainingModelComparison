# rf_training.py
import sys
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from database import models_DAOIMPL, model_metrics_history_DAOIMPL
from Models import model, model_metrics_history
from datetime import datetime

# Load preprocessed data
def load_preprocessed_data():
    with open('preprocessed_rf_data.pkl', 'rb') as f:
        preprocessed_data = pickle.load(f)
    return preprocessed_data

# Train and evaluate Random Forest model
def train_rf_model(model_name, user_id):
    # Load preprocessed data
    preprocessed_data = load_preprocessed_data()
    X_scaled = preprocessed_data['X_scaled']
    y = preprocessed_data['y']
    
    # Split the data
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
    
    # Train Random Forest Classifier
    rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_classifier.fit(X_train, y_train)

    # Evaluate the model
    y_pred = rf_classifier.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    print(f"Accuracy: {accuracy}")
    print(f"Precision: {precision}")
    print(f"Recall: {recall}")
    print(f"F1-Score: {f1}")

    # Save the model
    with open("rf_classifier.pkl", "wb") as model_file:
        pickle.dump(rf_classifier, model_file)
    with open("rf_classifier.pkl", "rb") as model_file:
        model_binary = model_file.read()

    # Insert model and metrics into the database
    new_model = model.Model(model_name, "Base metrics random forest model", model_binary, user_id, selected=1)
    model_exists = models_DAOIMPL.get_model_from_db_by_model_name_and_user_id(model_name, user_id)
    model_id = models_DAOIMPL.update_model_for_user(new_model, int(model_exists[0])) if model_exists else models_DAOIMPL.insert_model_into_models_for_user(new_model)
    
    # Insert metrics into the database
    new_history = model_metrics_history.Model_Metrics_History(model_id, accuracy, precision, recall, f1, '{}', datetime.now())
    model_metrics_history_DAOIMPL.insert_metrics_history(new_history)
    print("Model training and metrics storage complete.")

# Main execution
if __name__ == "__main__":
    model_name = 'RandomForestModel'
    if len(sys.argv) > 1:
        user_id = int(sys.argv[1])  # Convert argument to integer
    else:
        raise ValueError("User ID not provided. Please pass the user ID as a command-line argument.")

    train_rf_model(model_name, user_id)
