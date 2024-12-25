import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import alpaca_request_methods
from database import pending_orders_DAOIMPL, transactions_DAOIMPL, recommended_DAOIMPL, daily_balance_DAOIMPL, user_DAOIMPL, database_connection_utility as dcu
from Models import transaction, daily_balance
from datetime import date, datetime
import logging
from sector_finder import get_stock_sector

def check_order_completion(alpaca_conn:str,client_order_id:str) -> dict:
    ''' Check Alpaca REST API for buy order fill'''
    order = check_pending_order(alpaca_conn,client_order_id)
    if not order:
        return None
    if not order.filled_at:
        return None
    return order

def determine_if_order_is_buy_or_sell(order: dict) -> str:
    '''View order object to determine side type'''
    return order.side
    
def check_partial_fills_end_of_day(alpaca_conn:str,user_id:int,client_order_id:str) -> bool:
    ''' Check to see if there is a partial fill if 
        check buy order completion returns false.
        If partial exists create a transaction with only
        the partial fill quantity'''
    order = check_pending_order(alpaca_conn, client_order_id)
    if not order:
        return None
    qty = int(order.qty)
    filled_qty = order.filled_qty
    if not filled_qty:
        return None    
    filled_qty = int(filled_qty)
    if not (filled_qty != qty and filled_qty != 0):
        return None
    return order

def create_a_transaction_partial_fill_entry(partial_fill_data:dict) -> bool:
    ''' Create a transaction from Alpaca order data'''
    
    pass


def convert_a_buy_transaction_tuple_to_a_transaction_dictionary(transaction: tuple) -> dict:
    ''' Convert a database transaction tuple into a transaction
        dictionary object'''
    trans_dict = {
        'id':int(transaction[0]),
        'dp':transaction[1],
        'symbol':transaction[2],
        'ppps':round(float(transaction[3]),2),
        'qty':int(transaction[4]),
        'total_buy':round(float(transaction[5]),2),
        'pstring':transaction[6],
        'ds':None,
        'spps':None,
        'tsp':None,
        'sstring':None,
        'expected':round(float(transaction[11]),2),
        'proi':None,
        'actual':None,
        'tp1':round(float(transaction[14]),2),
        'sop':round(float(transaction[15]),2),
        'result':None,
        'user_id':int(transaction[17]),
        'sector':transaction[18],
        'processed':int(transaction[19]),
        'pol_neu_open':transaction[20],
        'pol_pos_open':transaction[21],
        'pol_neg_open':transaction[22],
        'sa_neu_open':transaction[23],
        'sa_pos_open':transaction[24],
        'sa_neg_open':transaction[25],
        'pol_neu_close':transaction[26],
        'pol_pos_close':transaction[27],
        'pol_neg_close':transaction[28],
        'sa_neu_close':transaction[29],
        'sa_pos_close':transaction[30],
        'sa_neg_close':transaction[31]
        
    }
    return trans_dict

def convert_a_sold_transaction_tuple_to_a_transaction_dictionary(transaction: tuple) -> dict:
    ''' Convert a database transaction tuple into a transaction
        dictionary object'''
    trans_dict = {
        'id':int(transaction[0]),
        'dp':transaction[1],
        'symbol':transaction[2],
        'ppps':round(float(transaction[3]),2),
        'qty':int(transaction[4]),
        'total_buy':round(float(transaction[5]),2),
        'pstring':transaction[6],
        'ds':transaction[7],
        'spps':round(float(transaction[8]),2),
        'tsp':round(float(transaction[9]),2),
        'sstring':transaction[10],
        'expected':round(float(transaction[11]),2),
        'proi':round(float(transaction[12]),2),
        'actual':round(float(transaction[13]),2),
        'tp1':round(float(transaction[14]),2),
        'sop':round(float(transaction[15]),2),
        'result':transaction[16],
        'user_id':int(transaction[17]),
        'sector':transaction[18],
        'processed':int(transaction[19]),
        'pol_neu_open':transaction[20],
        'pol_pos_open':transaction[21],
        'pol_neg_open':transaction[22],
        'sa_neu_open':transaction[23],
        'sa_pos_open':transaction[24],
        'sa_neg_open':transaction[25],
        'pol_neu_close':transaction[26],
        'pol_pos_close':transaction[27],
        'pol_neg_close':transaction[28],
        'sa_neu_close':transaction[29],
        'sa_pos_close':transaction[30],
        'sa_neg_close':transaction[31]
        
    }
    return trans_dict

def create_a_new_sell_transaction_based_on_partial_fill_order(transaction: dict) -> bool:
    ''' Create a new database transaction entry based
        on the key:values of a transaction dictionary'''
    pass

def create_a_new_buy_transaction_based_on_fill_order(alpaca_fill: dict, user_id:int) -> bool:
    ''' Create a new database transaction entry based
        on the key:values of a transaction dictionary'''
    ppps = float(alpaca_fill.filled_avg_price)
    qty = int(alpaca_fill.qty)
    total_buy = ppps * qty 
    expected = total_buy * .03
    tp1 = (ppps * .03 ) + ppps
    sop = ppps - (ppps * .01 )
        
    trans_dict = {
        'dp':date.today(),
        'symbol':alpaca_fill.symbol,
        'ppps':round(ppps,2),
        'qty':qty,
        'total_buy':round(total_buy,2),
        'pstring':alpaca_fill.client_order_id,
        'ds':None,
        'spps':None,
        'tsp':None,
        'sstring':None,
        'expected':round(expected,2),
        'proi':None,
        'actual':None,
        'tp1':round(tp1,2),
        'sop':round(sop,2),
        'result':None,
        'user_id':user_id,
        'sector':get_stock_sector(alpaca_fill.symbol),
        'processed':0,
        'pol_neu_open':0,
        'pol_pos_open':0,
        'pol_neg_open':0,
        'sa_neu_open':0,
        'sa_pos_open':0,
        'sa_neg_open':0,
        'pol_neu_close':0,
        'pol_pos_close':0,
        'pol_neg_close':0,
        'sa_neu_close':0,
        'sa_pos_close':0,
        'sa_neg_close':0
        
    }
    
    return trans_dict


def update_open_transaction_after_partial_fill(transaction: dict) -> bool:
    ''' Update an open transaction based on the new partial fill '''
    pass
def check_pending_order(alpaca_conn:str,client_order_id:str) -> dict:
    ''' Check Alpaca REST API for pending transaction order '''
    order = alpaca_conn.get_order_by_client_order_id(client_order_id)
    if not order:
        return None
    return order

def cancel_pending_order(alpaca_conn:str,order:dict) -> bool:
    '''Connect to Alpaca and Cancel pending order if exists '''
    result = alpaca_conn.cancel_order(order.order_id)
    if not result:
        return None
    return True
    

def add_daily_balance_for_user_BOD(alpaca_conn:str,user_id:int) -> bool:
    ''' Add a daily balance entry for user at beginning
        of the trade day.'''
    acnt = alpaca_conn.get_account()
    usr_equity = round(float(acnt.equity),2)
    new_db = daily_balance.DailyBalance(date.today(),usr_equity,user_id)
    if not daily_balance_DAOIMPL.insert_balance(new_db):
        return None
    return True

def update_daily_balance_for_user_EOD(alpaca_conn:str,user_id:int) -> bool:
    ''' Update the daily balance database entry for the user
        at the end of the day.'''
    acnt = alpaca_conn.get_account()
    usr_equity = round(float(acnt.equity),2)
    db =  daily_balance_DAOIMPL.get_daily_balances_for_user_by_date(user_id, date.today())
    if not db:    
        add_daily_balance_for_user_BOD(alpaca_conn, user_id)
    else:
        if not daily_balance_DAOIMPL.update_balance(usr_equity,int(db[0])):
            return None
        return True

def process_user(user: tuple) -> None:
    username = user['user_name']
    user_id = int(user['id'])
    time_now = datetime.now()
    alpaca_conn = alpaca_request_methods.create_alpaca_api(username)
    if time_now.hour == 9 and time_now.minute == 30:
        add_daily_balance_for_user_BOD(alpaca_conn,user_id)
    elif time_now.hour == 16 and time_now.minute == 0:
        update_daily_balance_for_user_EOD(alpaca_conn,user_id)
    pending_orders = pending_orders_DAOIMPL.get_all_pending_orders(user_id)
    if pending_orders:
        for po in pending_orders:
            trans_id = po[5]
            coid = po[1]
            try:
                order = check_order_completion(alpaca_conn,coid)
            except:
                continue
            if order:
                side = determine_if_order_is_buy_or_sell(order)
                if side == 'buy':
                    try:
                        new_trans = create_a_new_buy_transaction_based_on_fill_order(order, user_id)
                    except Exception as e:
                        logging.exception(f'Unable to create new buy trans: {e}')
                        print(f'{datetime.now()}: Unable to create new buy trans: {e}')
                    try:
                        transactions_DAOIMPL.insert_transaction(new_trans,po)
                    except Exception as e:
                        logging.exception(f'Unable to insert transaction: {e}')
                        print(f'{datetime.now()}: Unable to insert transaction: {e}')
                else:
                    sold_trans = transactions_DAOIMPL.get_transaction_by_id(trans_id)
                    trans_dict = convert_a_sold_transaction_tuple_to_a_transaction_dictionary(sold_trans)
                    trans_dict['ds'] = date.today()
                    trans_dict['spps'] = round(float(order.filled_avg_price),2)
                    trans_dict['tsp'] = round((int(order.qty)* trans_dict['spps']),2)
                    trans_dict['sstring'] = f'{po[4]}-sell'
                    trans_dict['proi'] = (trans_dict['tsp'] - trans_dict['total_buy']) / trans_dict['total_buy']
                    trans_dict['actual'] = trans_dict['tsp'] - trans_dict['total_buy']
                    trans_dict['result'] = 'profit' if trans_dict['actual'] > 0 else 'loss'
                    trans_dict['pol_neu_close']
                    trans_dict['pol_pos_close']
                    trans_dict['pol_neg_close']
                    trans_dict['sa_neu_close']
                    trans_dict['sa_pos_close']
                    trans_dict['sa_neg_close']
                    values = [trans_dict['ds'],trans_dict['spps'],trans_dict['tsp'],trans_dict['sstring'],trans_dict['proi'],
                              trans_dict['actual'],trans_dict['result'],trans_dict['pol_neu_close'],trans_dict['pol_pos_close'],
                              trans_dict['pol_neg_close'],trans_dict['sa_neu_close'],trans_dict['sa_pos_close'],trans_dict['sa_neg_close']]
                    
                    transactions_DAOIMPL.update_transaction(sold_trans[0],values)
                    pending_orders_DAOIMPL.delete_pending_order_after_fill(po[0],'sell',user_id)


if __name__ == '__main__':
    users = user_DAOIMPL.get_all_users()
    if not users:
        logging.info(f'{datetime.now()}: There are not any users.')
    else:
        for user in users:
            process_user(user)
            logging.info(f'{datetime.now()}: Processed all pending sell and purchase transactions for user {user["user_name"]}')
            print(f'{datetime.now()}: Processed all pending sell and purchase transactions for user {user["user_name"]}')
    time_now = datetime.now()
    if time_now.hour == 16 and time_now.minute == 0:
        pending_orders_DAOIMPL.truncate_pending_orders_at_eod()
        logging.info(f'{datetime.now()}: Truncated all pending transactions for today')
        print(f'{datetime.now()}: Truncated all pending transactions for today')
                            
                        
                        
                    
    
        
   