import model_trainer_predictor_methods
from database import transactions_DAOIMPL, metrics_DAOIMPL, manual_metrics_DAOIMPL
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
# transactions_DAOIMPL.update_transaction(312,['2024-09-11',18.19,36.38,'2024/09/06 09:31-2-17.75-buy-PHAT ~sell(1)',2.47,'0.88'])
# transactions_DAOIMPL.update_transaction(317,['2024-09-11',286.50,12319.50,'2024/09/10 12:30-43-291.62-buy-MCD ~sell(1)',-1.76,'-220.16'])
# transactions_DAOIMPL.update_transaction(311,['2024-09-10',154.38,7101.48,'2024/09/05 12:30-46-142.06-buy-ORCL ~sell(1)',8.67,'566.71'])
    # INSERT TRANSACTION
# trans1 = transaction.transaction('SN','2024-09-12',101.02,85,8586.69,'2024/09/12 12:30-85-101.02-buy-SN',expected_return=251.78,stop_loss_price=0.0,tp1=103.9821,tp2=106.00,sop=94.49,prediction=1)
# trans2 = transaction.transaction('GGAL','2024-09-12',43.51,198,8614.98,'2024/09/12 12:30-198-43.51-buy-GGAL',expected_return=261.50,stop_loss_price=0.0,tp1=44.83075,tp2=45.70125,sop=40.60,prediction=1)
# trans3 = transaction.transaction('MCD','2024-09-10',291.62,43,12539.66,'2024/09/10 12:30-43-291.62-buy-MCD',expected_return=378.18,stop_loss_price=0.00,tp1=300.4149,tp2=306.24825,sop=287.21)

# transactions_DAOIMPL.insert_transactions([trans1,trans2])

# avg = metrics_DAOIMPL.get_last_sector_breakdown()
# accuracy_values = [int(acc[0]) for acc in avg]
# print(avg[0])

# breakdowns = manual_metrics_DAOIMPL.get_last_sector_breakdown_rec()
# print(breakdowns)