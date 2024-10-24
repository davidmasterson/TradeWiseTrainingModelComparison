




import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import model_metrics_history_DAOIMPL, models_DAOIMPL
from Models import model_metrics_history, model
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

# Data Preparation: X (features), y (target)
def prepare_data(df, target_column, time_steps):
    # Ensure non-numeric columns are excluded
    numeric_df = df.select_dtypes(include=['float64', 'int64'])

    # Scaling the data
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(numeric_df)

    X, y = [], []
    for i in range(time_steps, len(scaled_data)):
        X.append(scaled_data[i-time_steps:i])
        y.append(scaled_data[i, target_column])

    X, y = np.array(X), np.array(y)
    return X, y, scaler


# Build the LSTM Model
def create_lstm_model(input_shape):
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(input_shape[1], input_shape[2])))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(units=25))
    model.add(Dense(units=1))  # Predict the stock price
    
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model


# Train the LSTM model
def train_lstm_model(model, X_train, y_train, epochs=20, batch_size=32):
    model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size)
    return model


# Predict using the trained model
def predict_lstm_model(model, X_test, scaler, num_features):
    # Make predictions
    predictions = model.predict(X_test)
    
    # Since the predictions only affect the target column, we need to create
    # a placeholder array for all features (to match the scaler's expected input shape)
    predictions_extended = np.zeros((predictions.shape[0], num_features))

    # Replace the target column (let's assume it's the first column) with predictions
    predictions_extended[:, 0] = predictions[:, 0]

    # Inverse transform using the scaler, but only the first column is meaningful
    predictions_scaled_back = scaler.inverse_transform(predictions_extended)
    
    # Return only the first column, as that corresponds to the target
    return predictions_scaled_back[:, 0]


# Testing phase using future data (date_sold and sold_pps)
def evaluate_with_sell_data(df_test, predictions, time_steps):
    accuracy_list, precision_list, recall_list, f1_list = [], [], [], []
    
    for i in range(len(predictions)):
        sell_price = df_test['sold_pps'].iloc[i + time_steps]  # Actual sell price
        sell_date = df_test['date_sold'].iloc[i + time_steps]  # Actual sell date
        tp1_price = df_test['tp1'].iloc[i + time_steps]  # Target price
        
        # Evaluate if the max predicted price within 12 days hits tp1
        predicted_hit = max(predictions[i:i+12]) >= tp1_price
        
        # Binary outcome: 1 if target hit, 0 otherwise
        y_pred = 1 if predicted_hit else 0
        
        # Compare with actual sell price and date_sold
        if sell_price >= tp1_price:  # If actual sell price hit tp1, it's a "hit"
            y_true = 1
        else:
            y_true = 0
        
        # Calculate metrics
        accuracy = accuracy_score([y_true], [y_pred])
        precision = precision_score([y_true], [y_pred], zero_division=0)
        recall = recall_score([y_true], [y_pred], zero_division=0)
        f1 = f1_score([y_true], [y_pred], zero_division=0)
        
        # Store metrics
        accuracy_list.append(accuracy)
        precision_list.append(precision)
        recall_list.append(recall)
        f1_list.append(f1)
    
    # Aggregate metrics over the entire test set
    avg_accuracy = np.mean(accuracy_list)
    avg_precision = np.mean(precision_list)
    avg_recall = np.mean(recall_list)
    avg_f1 = np.mean(f1_list)
    
    return avg_accuracy, avg_precision, avg_recall, avg_f1


# Prepare data and train the model
time_steps = 60  # 60 previous time steps for each prediction
df = pd.read_csv('/home/ubuntu/TradeWiseTrainingModelComparison/dataset.csv')  # Load your dataset here

# Prepare the input data (X) and target column (y)
X, y, scaler = prepare_data(df, target_column=3, time_steps=time_steps)  # Example with 3rd column as target

# Split into training and test sets
train_size = int(0.8 * len(X))
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]

# Align tp1 values for the test set
tp1_values = df['tp1'].values  # Extract the 'tp1' column as the target threshold
tp1_test_values = tp1_values[-len(y_test):]  # Slice the last entries to match the test set

# Create and train the LSTM model
lstm_model = create_lstm_model(X_train.shape)
lstm_model = train_lstm_model(lstm_model, X_train, y_train)

# Get predictions
predictions = predict_lstm_model(lstm_model, X_test, scaler, num_features=X_test.shape[2])

# Reload the dataset for evaluation (to get sold_pps and date_sold)
df_test = pd.read_csv('/home/ubuntu/TradeWiseTrainingModelComparison/dataset.csv')  # Reload the dataset for testing phase

# Evaluate the model using the actual future sell data
avg_accuracy, avg_precision, avg_recall, avg_f1 = evaluate_with_sell_data(df_test, predictions, time_steps=60)

# Output the results
print(f"Accuracy: {avg_accuracy}")
print(f"Precision: {avg_precision}")
print(f"Recall: {avg_recall}")
print(f"F1-Score: {avg_f1}")


model_name = 'LSTM Model'
top_features = '{"RSI": 0.3, "SMA": 0.2}'

from datetime import datetime



# serialize the model for storage in database using h5 format to include the weights
# Saving the model to HDF5 (this stores both architecture and weights)
lstm_model.save('lstm_model.h5')
# Serialize model to binary (HDF5 format)
with open("lstm_model.h5", "rb") as model_file:
    model_binary = model_file.read()
    model_file.close()
 
if len(sys.argv) > 1:
        user_id = sys.argv[1]
model_name = 'LSTM'
model_description = 'Base metrics LSTM model'
user_id = int(user_id)
# Insert the model into the database
new_model = model.Model(model_name,model_description, model_binary,user_id,selected = 1)
model_exists = models_DAOIMPL.get_model_from_db_by_model_name_and_user_id(new_model.model_name,user_id)
if model_exists:
    model_id = models_DAOIMPL.update_model_for_user(new_model,int(model_exists[0]))
else:
    model_id = models_DAOIMPL.insert_model_into_models_for_user(new_model)
new_history = model_metrics_history.Model_Metrics_History(model_id, avg_accuracy, avg_precision, 1, avg_f1, '{}', datetime.now())
model_metrics_history_DAOIMPL.insert_metrics_history(new_history)