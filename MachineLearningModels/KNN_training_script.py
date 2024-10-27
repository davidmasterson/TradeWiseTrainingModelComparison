# knn_training.py
import sys
import pickle
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from database import models_DAOIMPL, model_metrics_history_DAOIMPL
from Models import model, model_metrics_history
from datetime import datetime

# Load preprocessed data
def load_preprocessed_data():
    with open('preprocessed_data.pkl', 'rb') as f:
        preprocessed_data = pickle.load(f)
    return preprocessed_data

# Train and evaluate KNN model
def train_knn_model(model_name, user_id):
    # Load preprocessed data
    preprocessed_data = load_preprocessed_data()
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

    # Print results for confirmation
    print(f"Accuracy: {accuracy}")
    print(f"Precision: {precision}")
    print(f"Recall: {recall}")
    print(f"F1-Score: {f1}")

    # Save model and store in database
    with open('knn_model.pkl', 'wb') as model_file:
        pickle.dump(knn_model, model_file)

    # Load model for storage
    with open('knn_model.pkl', 'rb') as model_file:
        model_binary = model_file.read()

    # Insert model and metrics into database
    new_model = model.Model(model_name, "Base metrics KNN model", model_binary, user_id, selected=1)
    model_exists = models_DAOIMPL.get_model_from_db_by_model_name_and_user_id(model_name, user_id)
    model_id = models_DAOIMPL.update_model_for_user(new_model, int(model_exists[0])) if model_exists else models_DAOIMPL.insert_model_into_models_for_user(new_model)

    # Insert model metrics into database
    new_history = model_metrics_history.Model_Metrics_History(model_id, accuracy, precision, recall, f1, '{}', datetime.now())
    model_metrics_history_DAOIMPL.insert_metrics_history(new_history)
    print("Model training and metrics storage complete.")

# Main execution block
if __name__ == "__main__":
    model_name = 'KNN'
    if len(sys.argv) > 1:
        user_id = int(sys.argv[1])  # Convert argument to integer
    else:
        raise ValueError("User ID not provided. Please pass the user ID as a command-line argument.")

    train_knn_model(model_name, user_id)
