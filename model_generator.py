#!/usr/bin/env python
# coding: utf-8

# In[200]:


import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report


# In[201]:


# Read in and look at the data
df = pd.read_csv('stock_trans_data.csv')

df.head()


# In[202]:


# Function to calculate SMA5
def calculate_sma5(close_prices):
    sma5 = []
    for i in range(len(close_prices)):
        if i < 4:  # Predict the SMA5 for the first four dates
            sma5.append(close_prices[i])
        else:
            sma5.append(np.mean(close_prices[i-4:i+1]))
    return sma5

# Apply the function to the 'close' column
df['SMA5'] = df['close'].apply(lambda x: calculate_sma5(eval(x)))

# Inspect the result
df[['close', 'SMA5']].head()


# In[203]:


def calculate_sma20(close_prices):
    sma20 = []
    for i in range(len(close_prices)):
        if i < 19:  # Not enough data for SMA5
            sma20.append(close_prices[i])
        else:
            sma20.append(np.mean(close_prices[i-19:i+1]))
    return sma20

# Apply the function to the 'close' column
df['SMA20'] = df['close'].apply(lambda x: calculate_sma20(eval(x)))

# Inspect the result
df[['close', 'SMA20']].head()


# In[204]:


# Function to calculate SMA5 slope based on the previous 4 days
def calculate_sma5_slope_with_prediction(sma5_list):
    sma5_slope = []
    for i in range(len(sma5_list)):
        if i < 4:  # Predict the slope for the first four entries
            if i > 0:  # Calculate the slope between the first two available points
                predicted_slope = round((sma5_list[i] - sma5_list[i-1]) , 2)
            else:
                predicted_slope = 0  # If no prior data, assume flat slope
            sma5_slope.append(predicted_slope)
        else:
            # Slope = (SMA5[today] - SMA5[4 days ago]) / 4
            slope = round((sma5_list[i] - sma5_list[i-4]) / 4, 2)
            sma5_slope.append(slope)
    return sma5_slope

# Apply the function to the 'close' column
df['SMA5_Slope'] = df['SMA5'].apply(lambda x: calculate_sma5_slope_with_prediction(x))

# Inspect the result
df[['SMA5', 'SMA5_Slope']].head()


# In[205]:


# Function to calculate SMA5 slope based on the previous 4 days
def calculate_sma20_slope_with_prediction(sma20_list):
    sma20_slope = []
    for i in range(len(sma20_list)):
        if i < 19:  # Predict the slope for the first four entries
            if i > 0:  # Calculate the slope between the first two available points
                predicted_slope = round((sma20_list[i] - sma20_list[i-1]) , 2)
            else:
                predicted_slope = 0  # If no prior data, assume flat slope
            sma20_slope.append(predicted_slope)
        else:
            slope = round((sma20_list[i] - sma20_list[i-4]) / 19, 2)
            sma20_slope.append(slope)
    return sma20_slope

# Apply the function to the 'close' column
df['SMA20_Slope'] = df['SMA20'].apply(lambda x: calculate_sma20_slope_with_prediction(x))

# Inspect the result
df[['SMA20', 'SMA20_Slope']].head()


# In[206]:


from statistics import mode

# Create a new list of 1s and 0s. 1 = increase from one sma to the next days sma, 0 = decrease from on sma to the next days sma
def calculate_increases(lst):
    probabilities = []
    for i in range(len(lst) - 1):
        if lst[i] < lst[i + 1]:
            probabilities.append(1)
        else:
            probabilities.append(0)
    probabilities.append(0)
    most_common = mode(probabilities)
    return most_common

# create new SMA<value>_prob columns and SMA<value>_slope_prob columns based on the result of the calculate increase function.
def get_increase_probability_and_create_new_column(initial_column, created_column):
    probs = []
    for x in df[initial_column]:
        prob = calculate_increases(x)
        probs.append(prob)
    df[created_column] = probs

# create a list of column names to run this on
old_columns = ['SMA5', 'SMA20', 'SMA5_Slope', 'SMA20_Slope']
for name in old_columns:
    get_increase_probability_and_create_new_column(name, name+'_prob')
    
# Calculate summary statistics for 'open' and 'close' prices
df['open_mean'] = df['open'].apply(lambda x: np.mean(eval(x)))
df['open_std'] = df['open'].apply(lambda x: np.std(eval(x)))
df['close_mean'] = df['close'].apply(lambda x: np.mean(eval(x)))
df['close_std'] = df['close'].apply(lambda x: np.std(eval(x)))
df['SMA5_last'] = df['SMA5'].apply(lambda x: x[-1] if isinstance(x, list) else np.nan)
df['SMA20_last'] = df['SMA20'].apply(lambda x: x[-1] if isinstance(x, list) else np.nan)
df['SMA5_Slope_last'] = df['SMA5_Slope'].apply(lambda x: x[-1] if isinstance(x, list) else np.nan)
df['SMA20_Slope_last'] = df['SMA20_Slope'].apply(lambda x: x[-1] if isinstance(x, list) else np.nan)


# drop all columns that contains lists as their data
df = df.drop(['SMA5','SMA20','SMA5_Slope','SMA20_Slope','open','close','historical_dates'], axis=1)
# inspect the dataframe in its current state
df


# In[207]:


from sklearn.preprocessing import LabelEncoder
# Initialize the Label Encoder
label_encoder = LabelEncoder()
# Fit and transform the 'symbol' column
df['symbol_encoded'] = label_encoder.fit_transform(df['symbol'])
# Fit and transform the 'purchase_date' column
df['purchase_date_encoded'] = label_encoder.fit_transform(df['purchase_date'])
# Fit and transform the 'sell_date' column
df['sell_date_encoded'] = label_encoder.fit_transform(df['sell_date'])

# inspect the dataframe in its current state
df


# In[208]:


# Create a seperate dataframe for the rows that are still showing as the position being open. This will be used for prediction
future_df = df[(df['sell_price'].isna())]
future_df = future_df.copy()

# drop the open positions from the training and test data
df = df.dropna(subset=['sell_price'])


# Now you have the last 5 open and close prices as features for your model create model used for testing future data
X = df.drop(['hit_take_profit', 'symbol', 'purchase_date', 'sell_date'], axis=1)
y = df['hit_take_profit']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the Random Forest model
rf_model = RandomForestClassifier(random_state=42)
rf_model.fit(X_train, y_train)

# Make predictions and evaluate the model
y_pred = rf_model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
classification_rep = classification_report(y_test, y_pred)

print(f"Accuracy: {accuracy}")
print("Classification Report:\n", classification_rep)

future_df.to_csv('pre_future_predictions.csv', index=False)


import pickle
model_pkl_file = "RandomForestModel.pkl"  


with open(model_pkl_file, 'wb') as file:  
    pickle.dump(rf_model, file)






