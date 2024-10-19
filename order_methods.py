import MachineLearningModels.manual_alg_requisition_script
import alpaca_request_methods
from database import user_DAOIMPL, transactions_DAOIMPL, pending_orders_DAOIMPL
import logging
from datetime import datetime, date
from flask import session
import MachineLearningModels
from Models import transaction
import sector_finder


def submit_limit_order(username, incoming_order):
    try:
        conn = alpaca_request_methods.create_alpaca_api(username)
        user_id = session.get('user_id')
        order = conn.submit_order(
            symbol=incoming_order['symbol'],  # Example stock symbol
            qty=incoming_order['qty'],  # Quantity of shares to buy
            side=incoming_order['side'],  # "buy" or "sell"
            type=incoming_order['type'],
            limit_price=incoming_order['limit_price'],# Order type: "market" or "limit"
            time_in_force=incoming_order['tif'],  # day
            client_order_id=f"{datetime.now()}{incoming_order['symbol']}{incoming_order['qty']} {incoming_order['limit_price']}/{user_id}"
        )
        coid = order.id
        logging.info(f"Order submitted: {incoming_order}, order_id {order}")
        pending_orders_DAOIMPL.insert_pending_order(coid,user_id)
    except Exception as e:
        logging.info(f"Error placing order: {e}")
 
def place_sell_order(symbol, qty, price, transaction_id, username):
    """
    Place a sell order on Alpaca with a unique client_order_id based on transaction_id.
    """
    
    try:
        api = alpaca_request_methods.create_alpaca_api(username)
        limit_price = alpaca_request_methods.get_symbol_current_price(symbol)
        sell_order = api.submit_order(
            symbol=symbol,
            qty=qty,  # Quantity to sell
            side='sell',
            type='limit',
            limit_price= price,
            time_in_force='day',  # day
            client_order_id=f"sell-{symbol}-{qty}-{limit_price}-{datetime.now().strftime('%Y-%M-%d %H:%m:%S')}/{username} "  # Unique identifier for the order
        )
        print(f"Sell order placed for {symbol}. Transaction ID: {transaction_id}")
        return sell_order
    except Exception as e:
        print(f"Error placing sell order for {symbol}: {e}")
        return None
    

def check_for_filled_orders_by_order_id(order):
    conn = alpaca_request_methods.create_alpaca_api(session.get('user_name'))
    orders = conn.list_orders(status ='filled')
    if orders:
        for order in orders:
            modify_order_and_insert_transaction_to_db(order)
        
        
        
def modify_order_and_insert_transaction_to_db(order):
    user_id = session.get('user_id')
    symbol = order.symbol
    filled_qty = int(order.qty)
    filled_avg_price = float(order.filled_avg_price)
    side = order.side
    client_order_id = order.client_order_id
    logging.info(client_order_id)
    user_id = client_order_id.split('/')[1]
    username = session.get('user_name')
    if side == 'buy':
        logging.info(f"Order {client_order_id} filled for {filled_qty} shares of {symbol} at {filled_avg_price}. For USER: {user_id}")
        total_buy = float(filled_avg_price) * int(filled_qty)
        tp1 = (float(filled_avg_price) * .03)  + float(filled_avg_price)
        sop = float(filled_avg_price) - (float(filled_avg_price) * .01) 
        expected = total_buy * .03
        company_name = sector_finder.get_stock_company_name(symbol)
        sentiment = MachineLearningModels.manual_alg_requisition_script.request_articles(symbol,company_name)
        sentiment = MachineLearningModels.manual_alg_requisition_script.process_phrase_for_sentiment(sentiment, company_name)
        new_trans = transaction.transaction(symbol=symbol, 
                                            dp =date.today(), 
                                            ppps=filled_avg_price, 
                                            qty=filled_qty, 
                                            total_buy=total_buy, 
                                            pstring=client_order_id, 
                                            user_id=user_id, 
                                            expected=expected,
                                            tp1 = tp1, 
                                            sop=sop, 
                                            sentiment=sentiment)
        # insert into the transactions table
        transactions_DAOIMPL.insert_transaction(new_trans)
    elif side == 'sell':
        symbol = order.symbol
        client_order_id = order.client_order_id
        spps = float(order.filled_avg_price)
        qty = int(order.qty)
        tsp = spps * qty
        db_open_transaction = transactions_DAOIMPL.get_open_transaction_by_pstring_for_user(client_order_id, user_id)
        total_buy = float(db_open_transaction[5])
        sstring = client_order_id
        actual = tsp - total_buy
        proi = round((total_buy - tsp) / total_buy, 2)
        ds = date.today()
        id = db_open_transaction[0]
        result = 1 
        if actual < 0:
            result = 0
        transactions_DAOIMPL.update_transaction(id,[ds, spps, tsp, sstring, proi, actual, result])
        
        
         