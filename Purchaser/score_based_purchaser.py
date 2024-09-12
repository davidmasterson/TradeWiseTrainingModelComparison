import json

def fetch_sector_breakdown_from_db(type_of_breakdown):
    """
    Mock function that simulates fetching a sector breakdown from the database.
    Can fetch 'profits', 'losses', 'rec' (recommended), or 'nrec' (non-recommended).
    """
    if type_of_breakdown == "profits":
        # Mock sector breakdown JSON string for profits
        sector_breakdown_json = '{"Technology": 5, "Real Estate": 3, "Consumer Cyclical": 2, "Healthcare": 1}'
    elif type_of_breakdown == "losses":
        # Mock sector breakdown JSON string for losses
        sector_breakdown_json = '{"Technology": 2, "Real Estate": 4, "Consumer Cyclical": 3}'
    elif type_of_breakdown == "rec":
        # Mock sector breakdown JSON string for recommended
        sector_breakdown_json = '{"Technology": 4, "Real Estate": 1, "Consumer Cyclical": 2}'
    elif type_of_breakdown == "nrec":
        # Mock sector breakdown JSON string for non-recommended
        sector_breakdown_json = '{"Technology": 3, "Real Estate": 2}'
    return sector_breakdown_json

def get_stock_sector(symbol):
    """
    Mock function that returns the sector of a stock symbol.
    In real usage, this would query an API or database to return the stock's sector.
    """
    sector_mapping = {
        'AAPL': 'Technology',
        'AMZN': 'Consumer Cyclical',
        'GOOG': 'Technology',
        'MSFT': 'Technology',
        'TSLA': 'Consumer Cyclical',
        'SPG': 'Real Estate',
        'PFE': 'Healthcare'
    }
    return sector_mapping.get(symbol, None)

def purchase_symbol(symbol, sector, final_value, min_spend, max_spend):
    """
    Mock function to simulate purchasing a stock symbol based on the final value.
    If the score is 1, purchase the maximum amount; otherwise, calculate based on the score.
    """
    if final_value == 1:
        total_purchase = max_spend
    else:
        total_purchase = (min_spend * final_value) + min_spend

    print(f"Purchasing {symbol} in sector {sector} with total amount: ${total_purchase:.2f} (Final value: {final_value})")

def rank_sectors(sector_breakdown):
    """
    Ranks sectors based on the number of stocks in each sector, from most to least.
    Returns a dictionary where each sector is assigned a rank.
    """
    sorted_sectors = sorted(sector_breakdown.items(), key=lambda x: x[1], reverse=True)
    return {sector: rank for rank, (sector, _) in enumerate(sorted_sectors, 1)}

def process_symbols_for_purchase(symbols_list, min_spend, max_spend):
    # Step 1: Fetch and parse the sector breakdown JSON for profits, losses, rec, and nrec
    sector_breakdown_profits_json = fetch_sector_breakdown_from_db("profits")
    sector_breakdown_profits = json.loads(sector_breakdown_profits_json)
    
    sector_breakdown_loss_json = fetch_sector_breakdown_from_db("losses")
    sector_breakdown_loss = json.loads(sector_breakdown_loss_json)
    
    sector_breakdown_rec_json = fetch_sector_breakdown_from_db("rec")
    sector_breakdown_rec = json.loads(sector_breakdown_rec_json)
    
    sector_breakdown_nrec_json = fetch_sector_breakdown_from_db("nrec")
    sector_breakdown_nrec = json.loads(sector_breakdown_nrec_json)

    # Step 2: Rank sectors for profits, losses, rec, and nrec based on stock counts
    sector_ranking_profits = rank_sectors(sector_breakdown_profits)
    sector_ranking_loss = rank_sectors(sector_breakdown_loss)
    sector_ranking_rec = rank_sectors(sector_breakdown_rec)
    sector_ranking_nrec = rank_sectors(sector_breakdown_nrec)
    
    print(f"Sector ranking (profits): {sector_ranking_profits}")
    print(f"Sector ranking (loss): {sector_ranking_loss}")
    print(f"Sector ranking (recommended): {sector_ranking_rec}")
    print(f"Sector ranking (non-recommended): {sector_ranking_nrec}")
    
    # Step 3: Loop through each symbol and calculate values based on profits, losses, rec, and nrec
    for symbol in symbols_list:
        stock_sector = get_stock_sector(symbol)  # Get the sector of the current symbol
        
        if stock_sector:
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
            
            print(f"{symbol}: Final value = {final_value}")
            
            # Purchase the symbol based on the final value
            purchase_symbol(symbol, stock_sector, final_value, min_spend, max_spend)
        else:
            print(f"Sector information not found for symbol: {symbol}")

# Example usage
symbols_to_purchase = ['AAPL', 'AMZN', 'GOOG', 'MSFT', 'TSLA', 'SPG', 'PFE']
min_spend = 500  # Example minimum spend
max_spend = 1000  # Example maximum spend
process_symbols_for_purchase(symbols_to_purchase, min_spend, max_spend)
