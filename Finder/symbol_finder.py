import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import alpaca_request_methods
from datetime import datetime
import concurrent.futures
import time



def get_asset_price(asset_symbol):
    '''
    Custom function to get the most recent price of a stock symbol.
    Returns the price as a float or None if an error occurs.
    '''
    try:
        connection = alpaca_request_methods.get_alpaca_connection()
        bar = connection.get_latest_bar(asset_symbol)
        price = float(bar.c) 
        return price
    except Exception as e:
        print(f"Error fetching price for {asset_symbol}: {e}")
        return None


def get_list_of_tradeable_stocks(stock_exchange=['NYSE', 'NASDAQ']):
    '''
    Fetches a list of tradeable stock symbols for the specified exchanges.
    '''
    try:
        api_connection = alpaca_request_methods.get_alpaca_connection()
        active_assets = api_connection.list_assets(status='active')
        assets = [a.symbol for a in active_assets if a.exchange in stock_exchange]
        return assets
    except Exception as e:
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')}: Unable to get list of tradeable stocks for {stock_exchange} exchange due to {e}.")
    finally:
        api_connection.close()


def fetch_price_data_concurrently(symbols_list, min_price=6.00, max_workers=5):
    '''
    Fetches price data concurrently for all symbols using ThreadPoolExecutor.
    Filters assets with prices above min_price.
    Continues execution even if exceptions occur.
    '''
    assets = []
    count = 0

    def fetch_price(symbol):
        try:
            price = get_asset_price(symbol)
            if price is not None and price >= min_price:
                return [symbol, price]
        except Exception as e:
            print(f"Error processing symbol {symbol}: {e}")
        return None

    # Thread pool for parallel execution
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_symbol = {executor.submit(fetch_price, symbol): symbol for symbol in symbols_list}

        # Iterate over completed futures
        for future in concurrent.futures.as_completed(future_to_symbol):
            symbol = future_to_symbol[future]
            try:
                result = future.result()
                if result:
                    assets.append(result)
                count += 1
                print(f"{count}/{len(symbols_list)}: Processed {symbol}")
            except Exception as e:
                print(f"Error processing {symbol}: {e}")

    return assets


def sort_list_from_lowest_price_to_highest_price(assets_list):
    '''
    Sorts the list of assets by price from lowest to highest.
    '''
    try:
        sorted_data = sorted(assets_list, key=lambda x: x[1])
        return sorted_data
    except Exception as e:
        print(f"Error sorting data: {e}")
        return assets_list


# Example usage
if __name__ == '__main__':
    # Step 1: Fetch tradeable stocks
    symbols = get_list_of_tradeable_stocks()

    # Step 2: Fetch price data concurrently
    assets_with_prices = fetch_price_data_concurrently(symbols)

    # Step 3: Sort the assets by price
    sorted_assets = sort_list_from_lowest_price_to_highest_price(assets_with_prices)

    # Print the sorted result
    print(sorted_assets)
