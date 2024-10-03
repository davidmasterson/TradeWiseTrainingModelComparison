import model_trainer_predictor_methods
from database import transactions_DAOIMPL, metrics_DAOIMPL, user_DAOIMPL, database_connection_utility as dcu, user_preferences_DAOIMPL
import uuid
import alpaca_request_methods
from Hypothetical_Predictor import CSV_Writer, stock_data_fetcher, predict_with_pre_trained_model
from Models import transaction
import logging
from datetime import datetime
import order_methods

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
# transactions_DAOIMPL.update_transaction(318,['2024-09-20',105.98,9008.30,'2024/09/12 12:30-85-101.02-buy-SN~sell(1)',5.00,'421.61', 1])
# transactions_DAOIMPL.update_transaction(328,['2024-09-18',106.02,954.18,'2024/09/16 9:30-9-103.65-buy-SN~sell(3)',2.28,'21.32', 1])
# transactions_DAOIMPL.update_transaction(311,['2024-09-10',154.38,7101.48,'2024/09/05 12:30-46-142.06-buy-ORCL ~sell(1)',8.67,'566.71'])
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


# transs = transactions_DAOIMPL.get_open_transactions_for_user(7)
# print(transs)
order_methods.place_sell_order('XNET',140,5.00,'2024-10-03 14:30:07.604395XNET140 2.13,7','davidstage3')
# transactions = transactions_DAOIMPL.get_open_transactions_for_user(7)
# for trans in transactions:
#     print(trans)