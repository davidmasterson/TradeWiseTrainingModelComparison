import model_trainer_predictor_methods
from database import transactions_DAOIMPL, metrics_DAOIMPL, database_connection_utility as dcu
import uuid
import alpaca_request_methods
from Hypothetical_Predictor import CSV_Writer, stock_data_fetcher, predict_with_pre_trained_model
from Models import transaction

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
# transactions_DAOIMPL.update_transaction(313,['2024-09-10',51.04,2245.76,'2024/09/09 12:30-44-51.91-buy-CPB ~sell(1)',-1.68,'-38.28'])
# transactions_DAOIMPL.update_transaction(315,['2024-09-10',51.04,51.04,'2024/09/10 09:31-1-51.79-buy-CPB ~sell(1)',-1.45,'-0.75'])
# transactions_DAOIMPL.update_transaction(311,['2024-09-10',154.38,7101.48,'2024/09/05 12:30-46-142.06-buy-ORCL ~sell(1)',8.67,'566.71'])
    # INSERT TRANSACTION
# trans1 = transaction.transaction('CPB','2024-09-10',51.79,1,51.79,'2024/09/10 09:31-1-51.79-buy-CPB',expected_return=1.47,stop_loss_price=0.0,tp1=53.2613,tp2=54.2955,sop=51.06)
# trans2 = transaction.transaction('CMS','2024-09-10',69.55,180,12519.00,'2024/09/10 12:30-180-69.55-buy-CMS',expected_return=373.71,stop_loss_price=0.0,tp1=71.6262,tp2=73.0170,sop=67.64)
# trans3 = transaction.transaction('MCD','2024-09-10',291.62,43,12539.66,'2024/09/10 12:30-43-291.62-buy-MCD',expected_return=378.18,stop_loss_price=0.00,tp1=300.4149,tp2=306.24825,sop=287.21)

# transactions_DAOIMPL.insert_transactions([trans1,trans2,trans3])

# avg = metrics_DAOIMPL.get_last_sector_breakdown()
# accuracy_values = [int(acc[0]) for acc in avg]
# print(avg[0])

db_conn = dcu.get_aws_db_connection()
print(db_conn)