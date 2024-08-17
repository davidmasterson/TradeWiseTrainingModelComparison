from datetime import date

def read_in_transactions(file):
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
