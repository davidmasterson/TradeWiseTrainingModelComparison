from datetime import date, datetime
from database import database_connection_utility as dcu


import csv


def get_transactions_from_db():
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT * FROM transactions'''
    
    try:
        cur.execute(sql)
        trans = cur.fetchall()
        
        if trans:
            # Fetch column names from the cursor
            column_names = [i[0] for i in cur.description]
            
            # Write data to CSV
            with open('Model_Training/transactions.csv', 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                
                # Write the header (column names)
                csvwriter.writerow(column_names)
                
                # Write the transaction data
                csvwriter.writerows(trans)
                
            print("Transactions have been exported to 'transactions.csv'.")
        else:
            print("No transactions found.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        
    finally:
        cur.close()
        conn.close()


def read_in_transactions(file):
    global progress
    get_transactions_from_db()
    path = '/home/david/StockPricePredictorUsingLSTM'
    filepath = path+file
    with open(filepath, 'r') as trans_reader:
        lines = trans_reader.readlines()
        return [trans_reader, lines]
    
def convert_lines_to_transaction_info_for_DF(reader, lines):
    trans_df_initial_data = []
    count = 0
    for line in lines:
        seperated_line = line.split(',')
        if count != 0:
            symbol = seperated_line[1]
            purchase_date_string = seperated_line[2].split('-')
            purchase_price = float(seperated_line[3])
            sell_date_string = seperated_line[7].split('-') if seperated_line[8] != 'N/A' else 'N/A'
            sell_price = float(seperated_line[8]) if seperated_line[8] != 'N/A' else 'N/A'
            actual_return = float(seperated_line[13]) if seperated_line[8] != 'N/A' else 'N/A'
            purchase_date = date(int(purchase_date_string[0]),int(purchase_date_string[1]), int(purchase_date_string[2]))
            sell_date = date(int(sell_date_string[0]), int(sell_date_string[1]), int(sell_date_string[2])) if sell_price != 'N/A' else 'N/A'
            days_to_sell = (sell_date - purchase_date).days if seperated_line[8] != 'N/A' else 'N/A'
            take_profit = float(purchase_price + (purchase_price * .03)) if float(seperated_line[15]) == 0.00 else float(seperated_line[15])
            stop_price = float(purchase_price - (purchase_price * .01)) if float(seperated_line[14]) == 0.00 else float(seperated_line[14])
            hit_take_profit = 1 if actual_return != 'N/A' and actual_return > 0.00 else 0
            trans_df_initial_data.append([symbol,purchase_date,purchase_price,sell_date,sell_price,actual_return,days_to_sell,
                                        take_profit,stop_price,hit_take_profit])
        count += 1
    reader.close()
    return trans_df_initial_data


def insert_transactions(transactions):
    for transaction in transactions:
        insert_transaction(transaction)


def insert_transaction(transaction):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''
            INSERT INTO transactions
            (
            symbol,
            date_purchased,
            purchased_pps,
            qty,
            total_buy_price,
            purchase_string,
            date_sold,
            sold_pps,
            total_sell_price,
            sell_string,
            expected_return,
            percentage_roi,
            actual_return,
            stop_loss_price,
            tp1,
            tp2,
            sop
            ) VALUES (
            %s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s,
            %s,%s
            )
            '''
    vals = [transaction.symbol,
            transaction.date_purchased,
            transaction.purchased_pps,
            transaction.qty,
            transaction.total_buy_price,
            transaction.purchase_string,
            transaction.date_sold,
            transaction.sold_pps,
            transaction.total_sell_price,
            transaction.sell_string,
            transaction.expected_return,
            transaction.percentage_roi,
            transaction.actual_return,
            transaction.stop_loss_price,
            transaction.tp1,
            transaction.tp2,
            transaction.sop]
    try:
        cur.execute(sql,vals)
        conn.commit()
        print(f"{datetime.now()}:{cur.rowcount}, record inserted")
    except Exception as e:
        return e
    finally:
        cur.close()
        conn.close()

def update_transaction(transaction_id, values):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''
            UPDATE transactions
            SET
            date_sold = %s,
            sold_pps = %s,
            total_sell_price = %s,
            sell_string = %s,
            percentage_roi = %s,
            actual_return = %s
            WHERE
            transaction_id = %s
        '''
    vals = [values[0],
            values[1],
            values[2],
            values[3],
            values[4],
            values[5],
            transaction_id
            ]
    try:
        cur.execute(sql,vals)
        conn.commit()
        if cur.rowcount > 0:
            print(f"{cur.rowcount}, record(s) affected updated transaction {datetime.now()}id:{transaction_id}")
        else:
            print(f"{datetime.now()}:No record {transaction_id} has not been updated.")
    except Exception as e:
        return e
    finally:
        cur.close()
        conn.close()