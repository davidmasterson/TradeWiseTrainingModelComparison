import model_trainer_predictor_methods
from database import transactions_DAOIMPL
import uuid
import alpaca_request_methods
from Hypothetical_Predictor import CSV_Writer, stock_data_fetcher, predict_with_pre_trained_model
from Models import transaction

# with open('transactions.csv', 'r') as trans_reader:
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
    
    # transactions_DAOIMPL.insert_transactions(transactions)

    # UPDATE TRANSACTION
# transactions_DAOIMPL.update_transaction(302,['2024-08-27',63.32,4424.72,'2024/08/27 09:31-71-65.38-buy-VKTX',-4.63,'-214.43'])
    # INSERT TRANSACTION
# trans1 = transaction.transaction('VKTX','2024-08-27',65.34,71,4631.14,'2024/08/27 09:31-71-65.38-buy-VKTX',expected_return=109.92,stop_loss_price=0.0,tp1=66.8882,tp2=68.187,sop=62.67)
# trans2 = transaction.transaction('CLX','2024-08-27',154.90,30,4647.0,'2024/08/27 09:31-30-154.91-buy-CLX',expected_return=129.98,stop_loss_price=0.0,tp1=159.23,tp2=162.32,sop=150.26)
# trans3 = transaction.transaction('CL','2024-08-27',105.69,44,4650.35,'2024/08/27 12:30-44-105.71-buy-CL',expected_return=138.61,stop_loss_price=0.00,tp1=108.84,tp2=110.95,sop=103.88)

# transactions_DAOIMPL.insert_transactions([trans1,trans2,trans3])

