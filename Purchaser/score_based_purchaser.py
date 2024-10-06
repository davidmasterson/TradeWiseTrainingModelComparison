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

def process_symbols_for_purchase(symbols_list, min_spend, max_spend, min_total_spend, max_total_spend, username):
    
    user = user_DAOIMPL.get_user_by_username(username)[0]
    orders = {}
    # Fetch the last metric, if available
    last_metric = metrics_DAOIMPL.get_last_metric_for_user(user['id'])
    
    if last_metric:  # Check if the result is not empty
        last_metric = last_metric # Now safely access the first element
        
        # Step 1: Fetch and parse the sector breakdown JSON for profits, losses, rec, and nrec
        sector_breakdown_profits_json = fetch_sector_breakdown_from_db("profits", user['id'])
        sector_breakdown_profits = json.loads(sector_breakdown_profits_json)
        
        sector_breakdown_loss_json = fetch_sector_breakdown_from_db("losses", user['id'])
        sector_breakdown_loss = json.loads(sector_breakdown_loss_json)
        
        sector_breakdown_rec_json = fetch_sector_breakdown_from_db("rec", user['id'])
        sector_breakdown_rec = json.loads(sector_breakdown_rec_json)
        
        sector_breakdown_nrec_json = fetch_sector_breakdown_from_db("nrec", user['id'])
        sector_breakdown_nrec = json.loads(sector_breakdown_nrec_json)

        # Step 2: Rank sectors for profits, losses, rec, and nrec based on stock counts
        sector_ranking_profits = rank_sectors(sector_breakdown_profits)
        sector_ranking_loss = rank_sectors(sector_breakdown_loss)
        sector_ranking_rec = rank_sectors(sector_breakdown_rec)
        sector_ranking_nrec = rank_sectors(sector_breakdown_nrec)
        
        logging.info(f"Sector ranking (profits): {sector_ranking_profits}")
        logging.info(f"Sector ranking (loss): {sector_ranking_loss}")
        logging.info(f"Sector ranking (recommended): {sector_ranking_rec}")
        logging.info(f"Sector ranking (non-recommended): {sector_ranking_nrec}")
    
    else:
        logging.info("No metrics available for this user.")
        
    # Step 3: Loop through each symbol and calculate values based on profits, losses, rec, and nrec
    for symbol in symbols_list:
        stock_sector = get_stock_sector(symbol)  # Get the sector of the current symbol
        if last_metric:
            if stock_sector:
                final_value = ''
                # Handle profit ranking
                if stock_sector in sector_ranking_profits:
                    profit_position = sector_ranking_profits[stock_sector]
                    profit_value = 1 / profit_position
                else:
                    profit_value = 1  # Default to 1 if the sector is not found in profits
                
                # Handle loss ranking (subtract from profit value)
                if stock_sector in sector_ranking_loss:
                    loss_position = sector_ranking_loss[stock_sector]
                    loss_value = 1 / loss_position
                    final_value = profit_value - loss_value
                else:
                    final_value = profit_value  # No change if the sector is not found in the loss breakdown
                
                # Handle recommended ranking (add to final value)
                if stock_sector in sector_ranking_rec:
                    recommended_position = sector_ranking_rec[stock_sector]
                    recommended_value = 1 / recommended_position
                    final_value += recommended_value  # Add the recommended value
                
                # Handle non-recommended ranking (subtract from final value)
                if stock_sector in sector_ranking_nrec:
                    nrec_position = sector_ranking_nrec[stock_sector]
                    nrec_value = 1 / nrec_position
                    final_value -= nrec_value  # Subtract the non-recommended value
                limit_price = alpaca_request_methods.get_symbol_current_price(symbol) + .01   
               
                orders[symbol] = {
                    'symbol':symbol,
                    'limit_price':limit_price,
                    'qty':int(float((float(min_total_spend) * final_value) + float(min_total_spend))/limit_price),
                    'side':'buy',
                    'type':'limit',
                    'tif':'day',
                    'updated_last':datetime.now()
                }
            else:
                logging.info(f"Sector information not found for symbol: {symbol}")
                continue
            
        else:
        
            final_value = 1
            
            logging.info(f"{symbol}: Final value = {final_value}")
            limit_price = alpaca_request_methods.get_symbol_current_price(symbol) + .01
            # Purchase the symbol based on the final value
         
            orders[symbol] = {
                'symbol':symbol,
                'limit_price': limit_price,
                'qty': int(float(max_total_spend) / limit_price),
                'side':'buy',
                'type':'limit',
                'tif':'day',
                'updated_last': datetime.now()
            }
    return orders
            


# Example usage

