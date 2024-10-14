import json
from database import metrics_DAOIMPL, user_DAOIMPL
from sector_finder import get_stock_sector
import order_methods, alpaca_request_methods
from flask import session
import logging
from datetime import datetime, timezone

def fetch_sector_breakdown_from_db(type_of_breakdown,user_id):
    """
    Mock function that simulates fetching a sector breakdown from the database.
    Can fetch 'profits', 'losses', 'rec' (recommended), or 'nrec' (non-recommended).
    """
    model_metrics = metrics_DAOIMPL.get_last_metric_for_user(user_id)
    if model_metrics:
        if type_of_breakdown == "profits":
            # Mock sector breakdown JSON string for profits
            sector_breakdown_json = model_metrics[8]
        elif type_of_breakdown == "losses":
            # Mock sector breakdown JSON string for losses
            sector_breakdown_json = model_metrics[9]
        elif type_of_breakdown == "rec":
            # Mock sector breakdown JSON string for recommended
            sector_breakdown_json = model_metrics[10]
        elif type_of_breakdown == "nrec":
            # Mock sector breakdown JSON string for non-recommended
            sector_breakdown_json = model_metrics[11]
        return sector_breakdown_json
   


def purchase_symbol(symbol, sector, final_value, min_spend, max_spend):
    """
    Mock function to simulate purchasing a stock symbol based on the final value.
    If the score is 1, purchase the maximum amount; otherwise, calculate based on the score.
    """
    if final_value == 1:
        total_purchase = max_spend
    else:
        total_purchase = (min_spend * final_value) + min_spend

    logging.info(f"Purchasing {symbol} in sector {sector} with total amount: ${total_purchase:.2f} (Final value: {final_value})")

def rank_sectors(sector_breakdown):
    """
    Ranks sectors based on the number of stocks in each sector, from most to least.
    Returns a dictionary where each sector is assigned a rank.
    """
    sorted_sectors = sorted(sector_breakdown.items(), key=lambda x: x[1], reverse=True)
    return {sector: rank for rank, (sector, _) in enumerate(sorted_sectors, 1)}

def process_symbols_for_purchase(symbols_list, max_total_spend):
    
    
    orders = {}
    for symbol in symbols_list: 
        limit_price = float(alpaca_request_methods.get_symbol_current_price(symbol))
         
        limit_price = round(limit_price,2)
        orders[symbol] = {
            'symbol':symbol,
            'limit_price': float(limit_price),
            'qty': int(float(max_total_spend) / float(limit_price)),
            'side':'buy',
            'type':'limit',
            'tif':'day',
            'updated_last': datetime.now()
        }
    return orders
            


# Example usage

