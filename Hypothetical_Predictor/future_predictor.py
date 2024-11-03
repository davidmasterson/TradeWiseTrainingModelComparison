#!/usr/bin/env python
# coding: utf-8

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
import pickle
import sys
from database import models_DAOIMPL

user_id = int(sys.argv[1])



# import trained_model
ma_model = pickle.loads(models_DAOIMPL.get_trained_model_for_user_by_model_name(user_id, 'Manual Algorithm'))
future_df = pd.read_csv('Hypothetical_Predictor/transactions.csv')




# In[209]:


X_future = future_df.drop(['hit_take_profit', 'symbol', 'purchase_date', 'sell_date'], axis=1)
future_predictions = ma_model.predict(X_future)


# In[210]:


future_df['hit_take_profit_predicted'] = future_predictions

future_df.to_csv('Hypothetical_Predictor/future_predictions.csv', index=False)

# In[211]:





# In[212]:


future_probabilities = rf_model.predict_proba(X_future)
future_probabilities


# In[ ]: