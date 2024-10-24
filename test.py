import model_trainer_predictor_methods
from database import transactions_DAOIMPL, metrics_DAOIMPL, user_DAOIMPL, database_connection_utility as dcu, user_preferences_DAOIMPL, preprocessing_scripts_DAOIMPL, models_DAOIMPL,model_metrics_history_DAOIMPL, trade_settings_DAOIMPL
import uuid
import alpaca_request_methods
from Hypothetical_Predictor import CSV_Writer, stock_data_fetcher, predict_with_pre_trained_model
from Models import transaction, preprocessing_script, trade_setting
import logging
from datetime import datetime
import order_methods
from flask import session
from MachineLearningModels import manual_alg_requisition_script
from sector_finder import get_stock_sector, get_stock_company_name
import app

# with open('080724-transactiondata.csv', 'r') as trans_reader:
#     lines = trans_reader.readlines()
#     transactions = []
#     count = 0
#     for line in lines:
#         if count > 0:
#             line = line.split(',')
#             symbol = line[1]
#             purchased = line[2]
#             purchase_price = float(line[3])
#             qty = int(line[4])
#             total_purchase = float(line[5])
#             purchase_string = line[6]
#             sold_date = line[7]
#             sold_pps = float(line[8]) if line[8] != 'N/A' else line[8]
#             total_sell = float(line[9]) if line[9] != 'N/A' else line[9]
#             sell_string = line[10]
#             expected_return = float(line[11])
#             percentage_roi = float(line[12]) if line[12] != 'N/A' else line[12]
#             actual_return = float(line[13]) if line[13] != 'N/A' else line[13]
#             stop_loss_price = float(line[14])
#             tp1 = float(line[15])
#             tp2 = float(line[16])
#             sop = float(line[17])
#             new_trans = transaction.transaction(symbol, purchased,purchase_price,qty,total_purchase,purchase_string,sold_date,sold_pps,total_sell,sell_string,
#                                                 expected_return,percentage_roi,actual_return,stop_loss_price,tp1,tp2,sop)
#             transactions.append(new_trans)
#         count += 1
    
#     transactions_DAOIMPL.insert_transactions(transactions)

    # UPDATE TRANSACTION
# transactions_DAOIMPL.update_transaction(1,['2024-10-3',6.68,233.80,'2024-09-26 18:50:36.789194NVVE35 5.68,7~sell(1)',1,35.00, 1])
# transactions_DAOIMPL.update_transaction(2,['2024-10-3',7.21,230.72,'2024-09-26 18:50:33.097167EVTL32 6.21,7~sell(3)',1,32.00, 1])
# transactions_DAOIMPL.update_transaction(3,['2024-10-3',8.66,303.10,'2024-09-26 19:01:04.818726NVVE35 5.66,7~sell(1)',1,35.00,1])
    # INSERT TRANSACTION
# transactions = [
    # transaction.transaction('PYPL','2024-09-19',77.37,70,5415.90,'2024/09/19 12:30-70-77.37-buy-PYPL',expected_return=160.67,stop_loss_price=0.0,tp1=79.66535,tp2=81.21225,sop=370.99,prediction=0),
#     transaction.transaction('PLTR','2024-09-16',35.95,26,934.70,'2024/09/16 9:30-26-35.95-buy-PLTR',expected_return=29.91,stop_loss_price=0.0,tp1=37.1006,tp2=37.821,sop=34.40,prediction=1),
#     transaction.transaction('ZETA','2024-09-16',27.37,35,957.95,'2024/09/16 9:30-35-27.37-buy-ZETA',expected_return=26.57,stop_loss_price=0.0,tp1=28.1292,tp2=28.6755,sop=26.20,prediction=1),
#     transaction.transaction('CP','2024-09-16',86.94,11,956.33,'2024/09/16 9:30-11-86.96-buy-CP',expected_return=27.00,stop_loss_price=0.0,tp1=89.3937,tp2=91.1295,sop=85.06,prediction=0),
#     transaction.transaction('VNO','2024-09-16',36.60,26,951.60,'2024/09/16 9:30-26-36.60-buy-VNO',expected_return=26.40,stop_loss_price=0.0,tp1=37.6156,tp2=38.3460,sop=33.95,prediction=0),
#     transaction.transaction('BXP','2024-09-16',80.59,11,886.49,'2024/09/16 9:30-11-80.59-buy-BXP',expected_return=24.21,stop_loss_price=0.0,tp1=82.7914,tp2=84.399,sop=75.90,prediction=0),
#     transaction.transaction('SN','2024-09-16',103.65,9,932.85,'2024/09/16 9:30-9-103.65-buy-SN',expected_return=19.54,stop_loss_price=0.0,tp1=105.8222,tp2=107.877,sop=99.10,prediction=0),
#     transaction.transaction('BK','2024-09-16',69.29,13,900.77,'2024/09/16 9:30-13-69.29-buy-BK',expected_return=27.02,stop_loss_price=0.0,tp1=71.3687,tp2=72.7545,sop=67.8500,prediction=1),
#     transaction.transaction('WELL','2024-09-16',129.43,3,388.29,'2024/09/16 12:30-3-129.43-buy-WELL',expected_return=11.52,stop_loss_price=0.0,tp1=133.2716,tp2=135.8595,sop=128.05,prediction=1),
#     transaction.transaction('MCD','2024-09-16',296.63,1,296.63,'2024/09/16 12:30-1-296.63-buy-MCD',expected_return=8.85,stop_loss_price=0.00,tp1=305.4876,tp2=311.4194,sop=292.01,prediction=1)
# ]

# transactions_DAOIMPL.insert_transactions(transactions)

# avg = metrics_DAOIMPL.get_last_sector_breakdown()
# accuracy_values = [int(acc[0]) for acc in avg]
# logging.infoavg[0])

# conn = user_DAOIMPL.get_user_by_username('davidstage2')[0]
# id = conn['id']
# user_DAOIMPL.update_user_alpaca_keys('PK2OCFYFS8QN6RXFG2I8','CkiDGG3MWQbgv8Z9lCR2dudhKZbHMUrNn9RgRWpb',id)

# user_DAOIMPL.update_user_alpaca_keys('PKZBW6ION9J31KWUYTRW','WmzUgfZypTdbkYQG596ea9UTtwd2mKG3gyJwkGaa',7)
# user = transactions_DAOIMPL.get_open_transactions_for_user(7)
# print(user)


# Remove Testing Metrics
# conn = dcu.get_db_connection()
# cur = conn.cursor()
# sql = '''DELETE FROM metrics
# WHERE id= 1'''
# cur.execute(sql)
# conn.commit()
# conn.close()
# cur.close()
# preprocessing_scripts_DAOIMPL.create_preprocessing_scripts_table(7)
# cols = dcu.show_table_columns('model_metrics_history')
# print(cols)
# 

# model = models_DAOIMPL.get_trained_model_for_user(7)

# cols = dcu.show_table_columns('model_metrics_history')
# print(cols)



# create statements

# models = models_DAOIMPL.get_trained_model_names_for_user(7)
# print(models)
# model_metrics_history_DAOIMPL.create_model_metrics_history_table(7)
# model_trainer_predictor_methods.model_trainer(7)
# models_DAOIMPL.update_selected_models_for_user(7, 'RandomForestModel')
# models = model_metrics_history_DAOIMPL.get_most_recent_metric_for_user_selected_models(7)

# print(models)
# model_metrics_history_DAOIMPL.create_model_metrics_history_table(1)
# models_DAOIMPL.create_models_table()

# news =  manual_alg_requisition_script.request_articles('NVDA')
# sent = manual_alg_requisition_script.process_phrase_for_sentiment(news)
# for symbol in ['RKLB', 'CMP', 'CAE', 'RCEL']:
#     company_name = get_stock_company_name(symbol)
#     overall_sent = manual_alg_requisition_script.request_articles(symbol, company_name)
#     overall_sent = manual_alg_requisition_script.process_phrase_for_sentiment(overall_sent, company_name)
#     print(overall_sent)
# user_DAOIMPL.update_user_alpaca_keys('PKMIFIY4HCKE8FLGXQQB','FTs9KihbSjihd2bFlEs9Vit1pY15HFdorYZ2W4Q7',1)


# conn = alpaca_request_methods.create_alpaca_api('shadow073180')
# poss = conn.list_positions()
# for pos in poss:
#     transact = transactions_DAOIMPL.get_open_transactions_for_user_by_symbol(pos.symbol, 1)
#     if transact:
#         for trans in transact:
#             tp1 = float(trans[14])
#             sop = float(trans[15])
#             qty = int(trans[4])
#             buy_string = trans[6]
#             print(f'Position: {pos.symbol}, Price: {pos.current_price}, Take Profit: {tp1}, Stop Out: {sop}')
#             if float(pos.current_price) >= tp1 or float(pos.current_price) <= sop:
#                 order_methods.place_sell_order(pos.symbol,qty,pos.current_price,'shadow073180',buy_string )
from database import pending_orders_DAOIMPL

pending_orders_DAOIMPL.truncate_pending_orders_at_eod()