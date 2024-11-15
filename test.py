import model_trainer_predictor_methods
from database import (transactions_DAOIMPL, metrics_DAOIMPL, user_DAOIMPL, database_connection_utility as dcu,
                      user_preferences_DAOIMPL, preprocessing_scripts_DAOIMPL, models_DAOIMPL,
                      model_metrics_history_DAOIMPL, trade_settings_DAOIMPL)
import uuid
import alpaca_request_methods
from Hypothetical_Predictor import CSV_Writer, stock_data_fetcher, predict_with_pre_trained_model
from Models import transaction, preprocessing_script, trade_setting
import logging
from MachineLearningModels import manual_alg_requisition_script
from sector_finder import get_stock_sector, get_stock_company_name



'''Update user alpaca keys and endpoint'''
endpoint = ''
# user_DAOIMPL.update_user_alpaca_keys('PKD49UNWI3G7Y8E9708Y','PvbKSjLdZtWPOev6i6tzXRf0086gnAjRhxPDolYZ',1)


'''Make DS a blank pandas DataFrame'''
from database import dataset_DAOIMPL, preprocessing_scripts_DAOIMPL
from Models import dataset
import pickle
import pandas as pd
from datetime import datetime
finalized_dataset_data = dataset_DAOIMPL.get_dataset_data_by_id(35)
dsobject = dataset_DAOIMPL.get_dataset_object_by_id(35)
finalized_dataset_data = pickle.loads(finalized_dataset_data)
final_df = pd.DataFrame()
print(final_df)
final_df_bin = pickle.dumps(final_df)
newd = dataset.Dataset(dsobject[1],dsobject[2],final_df_bin,datetime.now(),6)
dataset_DAOIMPL.update_dataset(newd,35)


'''Get ppscript with correct X and columns from a ppscript that is correct and copy to the current users ppscript data column'''
# import pickle
# ppdata_bin = preprocessing_scripts_DAOIMPL.get_preprocessed_data_by_preprocessing_script_id(72)
# ppdata = pickle.loads(ppdata_bin)
# print(ppdata['columns'])
# new_bin = pickle.dumps(ppdata)
# preprocessing_scripts_DAOIMPL.update_preprocessed_data_for_user(73,new_bin)



'''Insert transaction that didn't get inserted by socket'''
# from datetime import datetime
# from datetime import date
# symbol = 'FBYDW'
# ppps = 1.00
# qty = 30
'''------------- Change these parameters only---------------'''
# dp = date(2024,11,12)
# total_buy = ppps * qty
# pstring = f'{datetime.now()}-{symbol}-{dp}-{ppps}-{qty}-{total_buy}'
# user_id = 2
# ds = None
# spps = None
# tsp = None
# sstring = None
'''--------------------------------------------------------------'''

# from database import pending_orders_DAOIMPL
# poid = pending_order = pending_orders_DAOIMPL.insert_pending_order(pstring,user_id,'buy',pstring)
# new_transaction = transaction.transaction(symbol, dp,ppps,qty,total_buy,pstring,user_id,ds,spps,tsp,sstring,expected = (total_buy * .03),proi=None,
#                                           actual=None,tp1 = ppps + (ppps * .03), sop = ppps - (ppps * .01), result = None, processed = 0)
# transactions_DAOIMPL.insert_transaction(new_transaction,poid)



''' Get sentiment analysis scores for however many symbols are in the symbols list'''
# symbols = ['ONCY']
# for symbol in symbols:
#     info = manual_alg_requisition_script.request_articles(symbol)
#     sa_neu, sa_pos, sa_neg = manual_alg_requisition_script.process_phrase_for_sentiment(info)
#     print(pol_neu, sa_pos, sa_neg)
# print(manual_alg_requisition_script.process_daily_political_sentiment())


'''Get Political climate scores for the day'''
# sa_neu, sa_pos, sa_neg = manual_alg_requisition_script.process_daily_political_sentiment()
# print(sa_neu, sa_pos, sa_neg)
