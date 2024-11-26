import model_trainer_predictor_methods
from database import (transactions_DAOIMPL, metrics_DAOIMPL, user_DAOIMPL, database_connection_utility as dcu,
                      user_preferences_DAOIMPL, preprocessing_scripts_DAOIMPL, models_DAOIMPL,
                      model_metrics_history_DAOIMPL, trade_settings_DAOIMPL, pending_orders_DAOIMPL, dataset_DAOIMPL)
import uuid
import alpaca_request_methods
from Hypothetical_Predictor import CSV_Writer, stock_data_fetcher, predict_with_pre_trained_model
from Models import transaction, preprocessing_script, trade_setting, model, dataset
import logging
from MachineLearningModels import manual_alg_requisition_script
from sector_finder import get_stock_sector, get_stock_company_name
from datetime import date, datetime
import MachineLearningModels
import pandas as pd
import pickle



'''Update user alpaca keys and endpoint'''
# endpoint = ''
# user_DAOIMPL.update_user_alpaca_keys('PKD49UNWI3G7Y8E9708Y','PvbKSjLdZtWPOev6i6tzXRf0086gnAjRhxPDolYZ',1)


'''Make DS a blank pandas DataFrame'''
# from database import dataset_DAOIMPL, preprocessing_scripts_DAOIMPL
# from Models import dataset
# import pickle
# import pandas as pd
# from datetime import datetime
# finalized_dataset_data = dataset_DAOIMPL.get_dataset_data_by_id(35)
# dsobject = dataset_DAOIMPL.get_dataset_object_by_id(35)
# finalized_dataset_data = pickle.loads(finalized_dataset_data)
# final_df = pd.DataFrame()
# print(final_df)
# final_df_bin = pickle.dumps(final_df)
# newd = dataset.Dataset(dsobject[1],dsobject[2],final_df_bin,datetime.now(),6)
# dataset_DAOIMPL.update_dataset(newd,35)


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
# '''------------- Change these parameters only---------------'''
# symbol = 'EMD'
# qty = 10
# ppps = 9.78
# total_buy = ppps * qty
# user_id = 6
# '''--------------------------------------------------------------'''
# dp = date(2024,11,19)
# pstring = f'{datetime.now()}-{symbol}-{dp}-{ppps}-{qty}-{total_buy}'
# ds = None
# spps = None
# tsp = None
# sstring = None

# from database import pending_orders_DAOIMPL
# pending_orders_DAOIMPL.insert_pending_order(pstring,user_id,'buy',pstring)
# new_transaction = transaction.transaction(symbol, dp,ppps,qty,total_buy,pstring,user_id,ds,spps,tsp,sstring,expected = (total_buy * .03),proi=None,
#                                           actual=None,tp1 = ppps + (ppps * .03), sop = ppps - (ppps * .01), result = None, processed = 0)
# pending = pending_orders_DAOIMPL.get_pending_buy_orders_by_user_id_and_client_order_id(user_id,new_transaction.pstring )
# transactions_DAOIMPL.insert_transaction(new_transaction,pending)


'''Close out a transaction that was not closed automatically by the system'''
# from datetime import datetime, date
# symbol = 'BAK'
# user_id = 4
# transaction_id = 93
# filled_avg_price = 5.36
# filled_qty = 5
# total_purchase = 25.08
# client_order_id = '2024-11-21 12:39:31.346610-BAK-2024-11-21-5.02-5-25.099999999999998'
# purchase_string = '2024-11-21 12:39:31.346610-BAK-2024-11-21-5.02-5-25.099999999999998'
# pending_orders_DAOIMPL.insert_pending_order(client_order_id, user_id, 'sell', purchase_string)
# pending_order = pending_orders_DAOIMPL.get_pending_sell_orders_by_user_id_and_client_order_id(user_id, client_order_id)
# ds = date(2024,11,25)

# # ----------------------------------------------
# tsp = filled_qty * filled_avg_price
# logging.info({ds})
# spps = filled_avg_price
# logging.info({filled_avg_price})
# tsp = filled_avg_price * filled_qty
# logging.info({tsp})
# logging.info({total_purchase})
# actual = tsp - total_purchase
# logging.info({actual})
# proi = round(actual / total_purchase, 2)
# logging.info({proi})
# result = 'loss' if actual <= 0 else 'profit'
# logging.info({result})
# sstring = f"{client_order_id}~sell({datetime.now()})"
# logging.info({sstring})
# logging.info({transaction_id})
# pol_neu_close, pol_pos_close, pol_neg_close = MachineLearningModels.manual_alg_requisition_script.process_daily_political_sentiment()

# info = MachineLearningModels.manual_alg_requisition_script.request_articles(symbol)
# sa_neu_close, sa_pos_close, sa_neg_close = MachineLearningModels.manual_alg_requisition_script.process_phrase_for_sentiment(info)

# values = [ds, spps, tsp, sstring, proi, actual, result,pol_neu_close,pol_pos_close,pol_neg_close,sa_neu_close,sa_pos_close,sa_neg_close ]
# logging.info(f' Updating transaction Symbol:{symbol} Transaction ID:{transaction_id}')
# transactions_DAOIMPL.update_transaction(transaction_id, values)
# pending_orders_DAOIMPL.delete_pending_order_after_fill(pending_order[0], pending_order[3], pending_order[2])



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

# from Selenium import selenium_file
# from datetime import date
# #load dataframe 
# import pandas as pd
# from multiprocessing import Pool
# import pandas as pd

# # Load dataframe



# # Worker function to process a single row

# count = 1
# # Load dataframe
# df = pd.read_csv('Total_df.csv')

# # Remove invalid dates
# df = df[df['dp'] != '0000-00-00']
# df = df[df['ds'] != '0000-00-00']

# # Convert columns to datetime
# df['dp'] = pd.to_datetime(df['dp'])
# df['ds'] = pd.to_datetime(df['ds'])

# Create formatted date columns
# df['formatted_buy_date'] = df['dp'].apply(lambda x: date(x.year, x.month, x.day))
# df['formatted_sell_date'] = df['ds'].apply(lambda x: date(x.year, x.month, x.day))
# df_length = len(df)
# Initialize columns for sentiment scores
# df['sa_neu_open'], df['sa_pos_open'], df['sa_neg_open'] = None, None, None
# df['pol_neu_open'], df['pol_pos_open'], df['pol_neg_open'] = None, None, None
# df['sa_neu_close'], df['sa_pos_close'], df['sa_neg_close'] = None, None, None
# df['pol_neu_close'], df['pol_pos_close'], df['pol_neg_close'] = None, None, None

# Iterate through rows and calculate sentiment
# for index, row in df.iterrows():
#     stock_symbol = row['symbol']
#     buy_date = row['formatted_buy_date']
#     sell_date = row['formatted_sell_date']

    # Get sentiment for buy date
    # sa_neu, sa_pos, sa_neg = selenium_file.get_historical_stock_specific_sentiment_scores(stock_symbol, buy_date)
    # df.at[index, 'sa_neu_open'] = sa_neu
    # df.at[index, 'sa_pos_open'] = sa_pos
    # df.at[index, 'sa_neg_open'] = sa_neg

    # pol_neu, pol_pos, pol_neg = selenium_file.get_historical_political_sentiment_scores(buy_date)
    # df.at[index, 'pol_neu_open'] = pol_neu
    # df.at[index, 'pol_pos_open'] = pol_pos
    # df.at[index, 'pol_neg_open'] = pol_neg

    # # Get sentiment for sell date
    # sa_neu, sa_pos, sa_neg = selenium_file.get_historical_stock_specific_sentiment_scores(stock_symbol, sell_date)
    # df.at[index, 'sa_neu_close'] = sa_neu
    # df.at[index, 'sa_pos_close'] = sa_pos
    # df.at[index, 'sa_neg_close'] = sa_neg

#     pol_neu, pol_pos, pol_neg = selenium_file.get_historical_political_sentiment_scores(sell_date)
#     df.at[index, 'pol_neu_close'] = pol_neu
#     df.at[index, 'pol_pos_close'] = pol_pos
#     df.at[index, 'pol_neg_close'] = pol_neg
#     print(f'Completed number {count} out of {df_length}')
#     count += 1

# # Remove unnecessary columns
# df1 = df.loc[:, ~df.columns.str.contains('^Unnamed')]
# df1.to_csv('Last_ever.csv')
# print(df1.columns.to_list())


# from multiprocessing import Pool
# import pandas as pd
# from datetime import date

# # Worker function to process a single row
# def process_row(row):
#     stock_symbol = row['symbol']
#     buy_date = row['formatted_buy_date']
#     sell_date = row['formatted_sell_date']

#     # Process buy date sentiment
#     sa_neu_open, sa_pos_open, sa_neg_open = selenium_file.get_historical_stock_specific_sentiment_scores(stock_symbol, buy_date)
#     pol_neu_open, pol_pos_open, pol_neg_open = selenium_file.get_historical_political_sentiment_scores(buy_date)

#     # Process sell date sentiment
#     sa_neu_close, sa_pos_close, sa_neg_close = selenium_file.get_historical_stock_specific_sentiment_scores(stock_symbol, sell_date)
#     pol_neu_close, pol_pos_close, pol_neg_close = selenium_file.get_historical_political_sentiment_scores(sell_date)

#     # Return the results as a dictionary
#     return {
#         'sa_neu_open': sa_neu_open, 'sa_pos_open': sa_pos_open, 'sa_neg_open': sa_neg_open,
#         'pol_neu_open': pol_neu_open, 'pol_pos_open': pol_pos_open, 'pol_neg_open': pol_neg_open,
#         'sa_neu_close': sa_neu_close, 'sa_pos_close': sa_pos_close, 'sa_neg_close': sa_neg_close,
#         'pol_neu_close': pol_neu_close, 'pol_pos_close': pol_pos_close, 'pol_neg_close': pol_neg_close
#     }
    
# def process_dataframe_in_parallel(df):
#     # Ensure the DataFrame is prepared (dates formatted, etc.)
#     df['formatted_buy_date'] = df['dp'].apply(lambda x: date(x.year, x.month, x.day))
#     df['formatted_sell_date'] = df['ds'].apply(lambda x: date(x.year, x.month, x.day))

#     # Convert DataFrame rows to dictionaries for easier processing
#     rows = df.to_dict('records')

#     # Use multiprocessing to process rows in parallel
#     with Pool(processes=4) as pool:  # Adjust 'processes' based on the number of CPU cores available
#         results = pool.map(process_row, rows)

#     # Merge the results back into the DataFrame
#     results_df = pd.DataFrame(results)
#     df = pd.concat([df.reset_index(drop=True), results_df.reset_index(drop=True)], axis=1)

#     return df

# def execute_historical_SA_and_POL(file):
#     # Load and clean the DataFrame
#     df = pd.read_csv(file)
#     df = df[df['dp'] != '0000-00-00']
#     df = df[df['ds'] != '0000-00-00']
#     df['dp'] = pd.to_datetime(df['dp'])
#     df['ds'] = pd.to_datetime(df['ds'])

#     # Process the DataFrame in parallel
#     df_processed = process_dataframe_in_parallel(df)

#     # Save or print the processed DataFrame
#     df1 = df_processed.loc[:, ~df_processed.columns.str.contains('^Unnamed')]
#     df1.to_csv('Total2_df.csv')
#     print(df1.columns.to_list())
    
# execute_historical_SA_and_POL('final_ds.csv')
'''Calculate target '''
# def calculate_target(row):
#     """
#     Determines if tp1 was hit before sop based on 'actual'.
#     - Returns 1 if 'actual' > 0 (tp1 hit before sop).
#     - Returns 0 if 'actual' <= 0 (sop hit before tp1 or no profit).
#     """
#     try:
#         actual = row['actual']
        
#         if pd.isnull(actual):
#             return 0  # Default to 0 if 'actual' is missing
        
#         return 1 if actual > 0 else 0
#     except Exception as e:
#         logging.error(f"Error calculating target for row {row}: {e}")
#         return 0
    
    
'''Load dataset object dataset data by dataset id'''
# pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)
# pp_bin = dataset_DAOIMPL.get_dataset_data_by_id(13)
# dataset_obj = dataset_DAOIMPL.get_dataset_object_by_id(13)
# df = pickle.loads(pp_bin)
# print(df)# # df.to_csv('historical_ds_base.csv')
# df.drop(['id', 'sa_neu_open','sa_pos_open','sa_neg_open','sa_neu_close','sa_pos_close','sa_neg_close','pol_neu_open',
#          'pol_pos_open','pol_neg_open','pol_neu_close','pol_pos_close','pol_neg_close'], axis=1, inplace=True)
# df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
# print(df.columns.to_list())
# df.drop(['ds','dp'], axis=1, inplace=True)
# df['hit_tp1'] = df.apply(calculate_target , axis=1)
# df['dp'] = pd.to_datetime(df['dp'])
# df['purchase_day'] = df['dp'].dt.day
# df['purchase_month'] = df['dp'].dt.month
# df['purchase_year'] = df['dp'].dt.year
# df['ds'] = pd.to_datetime(df['ds'])
# df['sell_day'] = df['ds'].dt.day
# df['sell_month'] = df['ds'].dt.month
# df['sell_year'] = df['ds'].dt.year
# df.drop(['actual'], axis=1, inplace=True)

# df.drop(['formatted_buy_date', 'formatted_sell_date','check4sa', 'processed','confidence', 'user_id','result','proi','expected',
#          'pstring','tsp','spps','sstring' ], axis=1, inplace=True)
# df = df.dropna()
# print(df.columns.to_list())
# print(df.isnull().sum())
'''Normalize all open political, close politcal, open sa, and close sa data.'''
# def normalize_all_pol_and_sa_data(dataframe):
#     # SET conditions that will be used for determining removal of rows
#     condition_open_political = (df['pol_neu_open'] == 0) & (df['pol_pos_open'] == 0) & (df['pol_neg_open'] == 0)
#     condition_close_political = (df['pol_neu_close'] == 0) & (df['pol_pos_close'] == 0) & (df['pol_neg_close'] == 0)
#     condition_open_sentiment = (df['sa_neu_open'] == 0) & (df['sa_pos_open'] == 0) & (df['sa_neg_open'] == 0)
#     condition_close_sentiment = (df['sa_neu_close'] == 0) & (df['sa_pos_close'] == 0) & (df['sa_neg_close'] == 0)

#     # SET combined conditions
#     combined_condition = (
#         condition_open_political |
#         condition_close_political |
#         condition_open_sentiment |
#         condition_close_sentiment
#     )

#     # SET dataframe as dataframe minus rows meeting removal condition
#     df = df[~combined_condition]

#     # Calculate sums of remaining political open/close and sa open/close combinations
#     pol_open_sum = df[['pol_neu_open', 'pol_pos_open', 'pol_neg_open']].sum(axis=1)

#     df['pol_neu_open_norm'] = df['pol_neu_open'] / pol_open_sum * 100
#     df['pol_pos_open_norm'] = df['pol_pos_open'] / pol_open_sum * 100
#     df['pol_neg_open_norm'] = df['pol_neg_open'] / pol_open_sum * 100

#     # Round the results to 2 decimal places
#     df['pol_neu_open_norm'] = df['pol_neu_open_norm'].round(2)
#     df['pol_pos_open_norm'] = df['pol_pos_open_norm'].round(2)
#     df['pol_neg_open_norm'] = df['pol_neg_open_norm'].round(2)

#     # Update the original columns if needed
#     df['pol_neu_open'] = df['pol_neu_open_norm']
#     df['pol_pos_open'] = df['pol_pos_open_norm']
#     df['pol_neg_open'] = df['pol_neg_open_norm']

#     # Drop the temporary columns
#     df = df.drop(columns=['pol_neu_open_norm', 'pol_pos_open_norm', 'pol_neg_open_norm'])


#     pol_close_sum = df[['pol_neu_close', 'pol_pos_close', 'pol_neg_close']].sum(axis=1)

#     df['pol_neu_close_norm'] = df['pol_neu_close'] / pol_close_sum * 100
#     df['pol_pos_close_norm'] = df['pol_pos_close'] / pol_close_sum * 100
#     df['pol_neg_close_norm'] = df['pol_neg_close'] / pol_close_sum * 100

#     # Round the results to 2 decimal places
#     df['pol_neu_close_norm'] = df['pol_neu_close_norm'].round(2)
#     df['pol_pos_close_norm'] = df['pol_pos_close_norm'].round(2)
#     df['pol_neg_close_norm'] = df['pol_neg_close_norm'].round(2)

#     # Update the original columns if needed
#     df['pol_neu_close'] = df['pol_neu_close_norm']
#     df['pol_pos_close'] = df['pol_pos_close_norm']
#     df['pol_neg_close'] = df['pol_neg_close_norm']

#     # Drop the temporary columns
#     df = df.drop(columns=['pol_neu_close_norm', 'pol_pos_close_norm', 'pol_neg_close_norm'])

#     sa_open_sum = df[['sa_neu_open', 'sa_pos_open', 'sa_neg_open']].sum(axis=1)

#     df['sa_neu_open_norm'] = df['sa_neu_open'] / sa_open_sum * 100
#     df['sa_pos_open_norm'] = df['sa_pos_open'] / sa_open_sum * 100
#     df['sa_neg_open_norm'] = df['sa_neg_open'] / sa_open_sum * 100

#     # Round the results to 2 decimal places
#     df['sa_neu_open_norm'] = df['sa_neu_open_norm'].round(2)
#     df['sa_pos_open_norm'] = df['sa_pos_open_norm'].round(2)
#     df['sa_neg_open_norm'] = df['sa_neg_open_norm'].round(2)

#     # Update the original columns if needed
#     df['sa_neu_open'] = df['sa_neu_open_norm']
#     df['sa_pos_open'] = df['sa_pos_open_norm']
#     df['sa_neg_open'] = df['sa_neg_open_norm']

#     # Drop the temporary columns
#     df = df.drop(columns=['sa_neu_open_norm', 'sa_pos_open_norm', 'sa_neg_open_norm'])

#     sa_close_sum = df[['sa_neu_close', 'sa_pos_close', 'sa_neg_close']].sum(axis=1)

#     df['sa_neu_close_norm'] = df['sa_neu_close'] / sa_close_sum * 100
#     df['sa_pos_close_norm'] = df['sa_pos_close'] / sa_close_sum * 100
#     df['sa_neg_close_norm'] = df['sa_neg_close'] / sa_close_sum * 100

#     # Round the results to 2 decimal places
#     df['sa_neu_close_norm'] = df['sa_neu_close_norm'].round(2)
#     df['sa_pos_close_norm'] = df['sa_pos_close_norm'].round(2)
#     df['sa_neg_close_norm'] = df['sa_neg_close_norm'].round(2)

#     # Update the original columns if needed
#     df['sa_neu_close'] = df['sa_neu_close_norm']
#     df['sa_pos_close'] = df['sa_pos_close_norm']
#     df['sa_neg_close'] = df['sa_neg_close_norm']

#     # Drop the temporary columns
#     df = df.drop(columns=['sa_neu_close_norm', 'sa_pos_close_norm', 'sa_neg_close_norm'])
#     df.to_csv('presave.csv')
#     print(df)
#     df_final = df
#     # df1 = pd.read_csv('Total_df.csv')
#     df_final = df_final.loc[:, ~df_final.columns.str.contains('^Unnamed')]
#     return df_final

'''Create dataset object and update dataset based on a dataset id lastly print columns list for df'''
# # df_final = pd.read_csv('presave.csv')
# new_ds = dataset.Dataset('MATP1pre_SAPOL', 'MATP1_preSAPOL'[2], pickle.dumps(df), datetime.now(),1)
# dataset_DAOIMPL.insert_dataset(new_ds)
# print(df.columns.to_list())


'''Handle trade update'''
# def handle_trade_updates(ws, event, data, username, user_id):
   
#     try:
#         logging.info(f"Starting handle_trade_updates for user {username}, event: {event}")
#         if data['event'] == 'fill':  # Ensure the event is 'fill'
#             logging.info(f"Processing fill event for symbol: {data['order']['symbol']}, user: {username}")
#             logging.info(f'''Trade update received: Symbol: {data['order']['symbol']} Quantity: {data['order']['filled_qty']} Price: {data['order']['filled_avg_price']}
#                         Side: {data['order']['side']} Client order ID: {data['order']['client_order_id']}''')
#             symbol = data['order']['symbol']
#             filled_qty = int(data['order']['filled_qty'])
#             filled_avg_price = float(data['order']['filled_avg_price'])
#             side = data['order']['side']
#             client_order_id = data['order']['id']
#             logging.info(f"Extracted details - Symbol: {symbol}, Quantity: {filled_qty}, Price: {filled_avg_price}, Side: {side}, Order ID: {client_order_id}")
#             logging.info(f'Logging client order id for user{username} due to new fill')
            
#             if side == 'buy':
#                 logging.info(f' User: {username} had a new buy total fill')
#                 # Handle buy side
#                 try:
#                     logging.info(f"Order {client_order_id} filled for {filled_qty} shares of {symbol} at {filled_avg_price}. For USER: {user_id}")
#                     total_buy = float(filled_avg_price) * int(filled_qty)
#                     tp1 = (float(filled_avg_price) * .03) + float(filled_avg_price)
#                     sop = float(filled_avg_price) - (float(filled_avg_price) * .01)
#                     expected = total_buy * .03
#                     logging.info(f' Initial variables created for user {username}\'s new filled order')
                    
#                     logging.info(f'Attempting to create new transaction object.')
#                     new_trans = transaction.transaction(
#                         symbol=symbol,
#                         dp=date.today(),
#                         ppps=filled_avg_price,
#                         qty=filled_qty,
#                         total_buy=total_buy,
#                         pstring=client_order_id,
#                         user_id=user_id,
#                         expected=expected,
#                         tp1=tp1,
#                         sop=sop
#                     )
#                     logging.info(f'New transaction object has been created for {username} due to new transaction purchase fill')
#                     # Insert the transaction
                    
#                     # pending_orders_DAOIMPL.insert_pending_order(client_order_id,user_id,side)
#                     logging.info(f'Fetching pending order for {symbol} for user {username} ')
#                     try:
#                         pending = pending_orders_DAOIMPL.get_pending_buy_orders_by_user_id_and_client_order_id(user_id, client_order_id)
#                         if pending:
#                             logging.info(f'Pending order found')
#                         else:
#                             logging.warning(f' Pending order was not found for {symbol} {filled_qty} for user {username}')
#                     except Exception as e:
#                         logging.error(f"Error fetching pending orders: {e}")
#                     try:
#                         logging.info(f'Attempting to add new transaction to database for user {username}')
#                         transactions_DAOIMPL.insert_transaction(new_trans, pending)
#                         logging.info(f'Transaction has been successfully added to database for user {username}')
#                     except Exception as e:
#                         logging.error(f'Error inserting transaction due to {e}')
#                     logging.info(f"{datetime.now()}: Deleting pending transaction")
#                 except Exception as e:
#                     logging.error(f"{datetime.now()}: Unable to insert transaction or delete pending transaction {client_order_id} due to {e}")
#             elif side == 'sell':
#                 # Handle sell side
#                 logging.info(f" Filled sell order has been filled for user {username} Order {client_order_id} filled for {filled_qty} shares of {symbol} at {filled_avg_price}.")
#                 logging.info(f'Attempting to get pending order for {symbol} {filled_qty} for user {username}')
#                 pending_order = pending_orders_DAOIMPL.get_pending_sell_orders_by_user_id_and_client_order_id(user_id,client_order_id)
#                 if pending_order:
#                     logging.info(f' Pending order found for {symbol} {filled_qty} for user {username}')
#                     purchase_string = pending_order[4]
#                     logging.info(f'Purchase string is {purchase_string}')
#                     pending_order_id = int(pending_order[0])
#                     logging.info(f'Pending order id is {pending_order_id}')
#                 logging.info(f' Getting open transactions for {purchase_string} for user {username}')    
#                 transaction2 = transactions_DAOIMPL.get_open_transaction_by_pstring_for_user(purchase_string, user_id)
#                 if transaction2:
#                     logging.info(f'Open transaction has been found for {purchase_string} for user {username}')
#                     ds = date.today()
#                     logging.info({ds})
#                     spps = filled_avg_price
#                     logging.info({filled_avg_price})
#                     tsp = filled_avg_price * filled_qty
#                     logging.info({tsp})
#                     total_purchase = float(transaction2[5])
#                     logging.info({total_purchase})
#                     actual = tsp - total_purchase
#                     logging.info({actual})
#                     proi = round(actual / total_purchase, 2)
#                     logging.info({proi})
#                     result = 'loss' if actual <= 0 else 'profit'
#                     logging.info({result})
#                     sstring = f"{client_order_id}~sell({datetime.now()})"
#                     logging.info({sstring})
#                     transaction_id = int(transaction2[0])
#                     logging.info({transaction_id})
#                     pol_neu_close, pol_pos_close, pol_neg_close = MachineLearningModels.manual_alg_requisition_script.process_daily_political_sentiment()
#                     logging.info(f'Political scores{pol_neu_close, pol_pos_close, pol_neg_close}')
#                     logging.info(f'Fetching SA articles for user {username} Transaction {transaction_id}')
#                     info = MachineLearningModels.manual_alg_requisition_script.request_articles(symbol)
#                     logging.info(f'SA articles found for user {username} Transaction {transaction_id}')
#                     sa_neu_close, sa_pos_close, sa_neg_close = MachineLearningModels.manual_alg_requisition_script.process_phrase_for_sentiment(info)
#                     logging.info(f'SA scores {sa_neu_close, sa_pos_close, sa_neg_close} for {username} Transaction {transaction_id}')
                    
#                     values = [ds, spps, tsp, sstring, proi, actual, result,pol_neu_close,pol_pos_close,pol_neg_close,sa_neu_close,sa_pos_close,sa_neg_close ]
#                     logging.info(f' Updating transaction Symbol:{symbol} Transaction ID:{transaction_id}')
#                     transactions_DAOIMPL.update_transaction(transaction_id, values)
#                     logging.info(f'Successfully updated transaction. Now deleting pending order {pending_order_id}')
#                     pending_orders_DAOIMPL.delete_pending_order_after_fill(pending_order[0], pending_order[3], pending_order[2])
#                     logging.info(f'Pending order id {pending_order_id} successfully deleted')
#         else:
#             logging.warning(f"Unhandled event: {event}")
#     except Exception as e:
#         logging.error(f'Unable to handle trade updates due to {e}')


# '''Check preprocessing script for correct number of expected feature'''
# ppscript_bin = preprocessing_scripts_DAOIMPL.get_preprocessed_data_by_preprocessing_script_id(83)
# ppscript = pickle.loads(ppscript_bin)
# print(ppscript['columns'])











# 'ppps', 'qty', 'total_buy', 'tp1', 'sop', 'pol_neu_open', 
# 'pol_pos_open', 'pol_neg_open', 'sa_neu_open', 'sa_pos_open', 
# 'sa_neg_open', 'pol_neu_close', 'pol_pos_close', 'pol_neg_close', 
# 'sa_neu_close', 'sa_pos_close', 'sa_neg_close', 'check1sl', 
# 'check2rev', 'check3fib', 'check5con', 'purchase_day', 'purchase_month', 
# 'purchase_year', 'sell_day', 'sell_month', 'sell_year', 'symbol_encoded', 
# 'sector_encoded'

# 'ppps', 'qty', 'total_buy', 'tp1', 'sop', 'check1sl', 
# 'check2rev', 'check3fib',  'check5con', 'purchase_day', 
# 'purchase_month', 'purchase_year', 'symbol_encoded', 'sector_encoded',
# 'pol_neu_open','pol_pos_open','pol_neg_open'

# 'sell_day','sell_month','sell_year','pol_neu_open','pol_pos_open', 
# 'pol_neg_open', 'sa_neu_open', 'sa_pos_open', 
# 'sa_neg_open', 'pol_neu_close', 'pol_pos_close', 'pol_neg_close', 
# 'sa_neu_close', 'sa_pos_close', 'sa_neg_close',


'''fake info to test with'''
# username = 'sb2user4'
# user_id = 5
# ws = ' '
# import json
# data=b'{"stream":"trade_updates","data":{"event":"fill","timestamp":"2024-11-19T14:47:05.721Z","order":{"id":"6a7f7003-57fc-4ec5-bb8d-aa7730c49213","client_order_id":"sell-GNL-4-7.185-2024-47-19 09:11:05/sb2User4 ","created_at":"2024-11-19T14:47:05.706757064Z","updated_at":"2024-11-19T14:47:05.727883993Z","submitted_at":"2024-11-19T14:47:05.709346899Z","filled_at":"2024-11-19T14:47:05.721Z","expired_at":null,"cancel_requested_at":null,"canceled_at":null,"failed_at":null,"replaced_at":null,"replaced_by":null,"replaces":null,"asset_id":"b94e2aa2-2e40-4827-b660-f4d22d59c3d5","symbol":"GNL","asset_class":"us_equity","notional":null,"qty":"4","filled_qty":"4","filled_avg_price":"7.1831","order_class":"","order_type":"limit","type":"limit","side":"sell","time_in_force":"day","limit_price":"7.18","stop_price":null,"status":"filled","extended_hours":false,"legs":null,"trail_percent":null,"trail_price":null,"hwm":null},"price":"7.1831","qty":"4","position_qty":"0","execution_id":"d93c6c67-e216-4053-acfa-7967692a1a34"}}' 
# data_string = data.decode('utf-8')
# data = json.loads(data_string)

# handle_trade_updates(ws, data['data']['event'], data['data'], username, user_id)
# from Models import user_role
# from database import user_roles_DAOIMPL, roles_DAOIMPL
# role_id = roles_DAOIMPL.get_role_id_by_role_name('retail',1)
# new_role = user_role.UserRole(6,role_id)
# user_roles_DAOIMPL.insert_user_role(new_role, 1)


# user = user_DAOIMPL.get_all_users()
# print(user)

from HistoricalFetcherAndScraper import scraper

sa_neu, sa_pos, sa_neg = scraper.get_sa(date.today(),'KITT',1)
print(sa_neu, sa_pos, sa_neg)
