from copy import deepcopy
from datetime import datetime, timedelta
import tqdm
import alpaca_request_methods



def get_positions_to_buy(assets): 
    asset_list = []       
    count = 1
    if len(assets) > 0:
        for asset in assets:
            result = check_asset(asset)
            if result:
                asset_list.append(result)
            count += 1
                    
    else:
        print("No assets available for trading, there was an issue getting them from the api.")
        return []
    return asset_list

def check_asset(asset):
    try:
        symbol = asset[0]
        price = asset[1]
        
        second_check = second_check_engulfing_candle_with_reversal(asset)
        if second_check[0] == True: 
            # last_25 = get_last_25_day_closes(symbol)
            # if third_check_fibonacci_condition(last_25,symbol):
            print('passed all checks')
            return [symbol,price]
            #  Falsereturn
    except Exception as e:
        return False
    
    
    
def get_asset_7_day_volume_average(asset):
    volume_list = get_volume_list(asset,7,[],from_date=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),to_date=(datetime.now()).strftime("%Y-%m-%d"))
    if volume_list != None and len(volume_list) == 7:      
        avg_volume = float(sum(volume_list) / 7)
        avg_volume = "{:.4f}".format(avg_volume)
        return float(avg_volume)
    else:
        return None
    
def second_check_engulfing_candle_with_reversal(asset):
    last_four_candles = get_last_4__closes_full_candle_detail(asset)
    try:
        reversal_present = look_for_engulfing_candle_long_reversal(last_four_candles,asset)
        return [reversal_present,last_four_candles]
    except Exception as e:
        print(e)
        pass
    
def get_last_25_day_closes(position):
    symbol = position
    sma_list = get_sma_list(symbol,25,[],(datetime.now() - timedelta(days=25)).strftime("%Y-%m-%d"),datetime.now().strftime("%Y-%m-%d"))
    if len(sma_list) != None and sma_list != []:
        return sma_list
    


def third_check_fibonacci_condition(sma_list, symbol):
    if len(sma_list) < 5:
        print("Not enough data points for analysis.")
        return False

    # Sort the SMA list to get key points without modifying the original list
    sorted_sma = sorted(sma_list)
    lowest_low = sorted_sma[0]
    highest_high = sorted_sma[-1]
    secondary_high = sorted_sma[-2]
    secondary_low = sorted_sma[1]
    third_low = sorted_sma[2]

    # Calculate Fibonacci retracement levels based on the lowest low and highest high
    fib_levels = calculate_fibonacci_levels(lowest_low, highest_high)

    # Check if secondary points align with any Fibonacci retracement levels
    if any(secondary_high <= level <= highest_high for level in fib_levels) and any(lowest_low <= level <= secondary_low for level in fib_levels):
        print(f"Secondary points for {symbol} are within Fibonacci retracement levels.")
        
        # Check if third_low is within any Fibonacci retracement levels
        if any(lowest_low <= level <= third_low for level in fib_levels):
            print(f"Third low for {symbol} aligns with a Fibonacci retracement level.")
            return True

    print("No Fibonacci retracement conditions met.")
    return False

def calculate_fibonacci_levels(low, high):
    """
    This function calculates and returns Fibonacci retracement levels between a given low and high price.
    """
    range = high - low
    return [low + range * factor for factor in (0.236, 0.382, 0.5, 0.618, 0.786)]


# TODO pre_purchase_probability_checker

def get_volume_list(position,sma_number,volumes,from_date,to_date,recursion_count= 0):
    '''
        @position : Position
        @sma_number: Int
        @volumes: List
        @from_date : Datetime
        @to_date : Datetime
        @recursion_count : Int
        Based on the sma value this gets all volumes from each day at closing values within a weeks time frame and if the the 
        first returned result doesn't equal the sma value it will recursively modify the start date to add an additional number 
        of days needed to get to the sma value.'''
    recursion_count = recursion_count
    api_connection = alpaca_request_methods.get_alpaca_connection()
    volumes = volumes
    
    try:
        if query_string != None and len(query_string) == sma_number:                
            for item in query_string:
                query_string = api_connection.get_bars(position.symbol,timeframe='1Day',start=from_date,end=to_date,limit=sma_number)
                volumes.append(item.v)                
        elif len(query_string) < sma_number:
                new_from_date = (datetime.strptime(from_date,'%Y-%m-%d') - timedelta(days=sma_number - len(query_string))).strftime('%Y-%m-%d')
                recursion_count += 1  
                if recursion_count <= 30:      
                    get_volume_list(position,sma_number,volumes,from_date=new_from_date,to_date=to_date,recursion_count=recursion_count)
                else:
                    return None
        return volumes
    except Exception as e:
        print(f'{datetime.now()}:couldnt get volumes list for position {position.symbol} due to {e}')
        pass
    
def get_last_4__closes_full_candle_detail(position):
    symbol = position[0]
    sma_list = get_day_candles_with_main_account(symbol,4,[],(datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d"),datetime.now().strftime("%Y-%m-%d"))
    if len(sma_list) != None and sma_list != []:
        return sma_list
    

def look_for_engulfing_candle_long_reversal(day_close_candle_list,symbol):
    cand_2_open_price = float(day_close_candle_list[1].o)
    cand_2_hi_price = float(day_close_candle_list[1].h)
    cand_2_low_price = float(day_close_candle_list[1].l)
    cand_2_close_price = float(day_close_candle_list[1].c)

    cand_3_open_price = float(day_close_candle_list[2].o)
    cand_3_hi_price = float(day_close_candle_list[2].h)
    cand_3_low_price = float(day_close_candle_list[2].l)
    cand_3_close_price = float(day_close_candle_list[2].c)

    cand_4_open_price = float(day_close_candle_list[3].o)
    cand_4_hi_price = float(day_close_candle_list[3].h)
    cand_4_low_price = float(day_close_candle_list[3].l)
    cand_4_close_price = float(day_close_candle_list[3].c)
    # Red candle as candle 2
    engulfing_red_to_green_eng = (cand_2_open_price > cand_2_close_price and cand_3_open_price < cand_2_close_price and cand_3_close_price > cand_2_open_price and cand_3_close_price > cand_3_open_price)
    engulfing_green_to_green_eng = (cand_2_open_price < cand_2_close_price and cand_3_open_price <= cand_2_open_price and cand_3_close_price >= cand_2_close_price and cand_3_close_price > cand_3_open_price)
    reversal_candle = cand_4_open_price >= cand_3_close_price and cand_4_open_price < cand_4_close_price

    if engulfing_red_to_green_eng or engulfing_green_to_green_eng:
        print(f"{symbol} passed engulfing check")
        if reversal_candle:
            print(f"{symbol} passed reversal check")
            upward_trend = first_condition_slope_checks(symbol)
            if upward_trend:
                print(f'{symbol} passed upward trend condition and has passed all checks, adding to recommendations.')
                return True
    return False


# RECURSIVE method to get sma's
def get_sma_list(symbol,sma_number,closes,from_date,to_date,count = 0): 
    '''A recursive method to get an accurate return amount of close values for a given stock based on the Moving average line declaration.
    This method I created because that api doesn't take into account non trade days when adding a to and from date.'''       
    closes = closes
    symbol = symbol[0]
    api_connection = alpaca_request_methods.get_alpaca_connection()
    query_string = api_connection.get_bars(symbol,timeframe='1Day',start=from_date,end=to_date,limit=sma_number)
    try:
        if query_string != None and len(query_string) == sma_number:                
            for item in query_string:
                closes.append(item.c)                
        elif len(query_string) < sma_number:
            count += 1
            new_from_date = (datetime.strptime(from_date,'%Y-%m-%d') - timedelta(days=sma_number - len(query_string))).strftime('%Y-%m-%d') 
            if datetime.strptime(from_date,'%Y-%m-%d') < datetime(2016,1,1) and datetime.strptime(new_from_date,'%Y-%m-%d') < datetime(2016,1,1):
                new_from_date = "2016-01-01"
                get_sma_list(symbol,sma_number,closes,from_date=new_from_date,to_date=to_date,count=count)
            elif datetime.strptime(from_date,'%Y-%m-%d') == datetime(2016,1,1) and datetime.strptime(new_from_date,'%Y-%m-%d') < datetime(2016,1,1) or count >= 200: 
                return query_string
            else:
                get_sma_list(symbol,sma_number,closes,from_date=new_from_date,to_date=to_date,count=count)
        return closes
    except Exception as e:
        print(f'{datetime.now()}:couldnt get sma list for symbol {symbol} due to {e}')
        pass
    finally:
        api_connection.close()
        

def group_smas(sma_list):
    final_grouping = []
    count = 1
    cur_grouping = []
    for sma in sma_list: 
        cur_grouping.append(sma)
        if count % 5 == 0:
            final_grouping.append(cur_grouping)
            cur_grouping = []
        count += 1
    return final_grouping


def get_day_candles_with_main_account(symbol,sma_number,closes,from_date,to_date,count = 0, session=None): 
    '''A recursive method to get an accurate return amount of close values for a given stock based on the Moving average line declaration.
    This method I created because that api doesn't take into account non trade days when adding a to and from date.'''       
    closes = closes
    api_connection = alpaca_request_methods.get_alpaca_connection()
    query_string = api_connection.get_bars(symbol,timeframe='1Day',start=from_date,end=to_date,limit=sma_number)
    try:
        if query_string != None and len(query_string) == sma_number:                
            for item in query_string:
                closes.append(item)                
        elif len(query_string) < sma_number:
            count += 1
            new_from_date = (datetime.strptime(from_date,'%Y-%m-%d') - timedelta(days=sma_number - len(query_string))).strftime('%Y-%m-%d') 
            if datetime.strptime(from_date,'%Y-%m-%d') > datetime(2016,1,1) and datetime.strptime(new_from_date,'%Y-%m-%d') < datetime(2016,1,1):
                new_from_date = "2016-01-01"
                get_day_candles_with_main_account(symbol,sma_number,closes,from_date=new_from_date,to_date=to_date,count=count)
            elif datetime.strptime(from_date,'%Y-%m-%d') == datetime(2016,1,1) and datetime.strptime(new_from_date,'%Y-%m-%d') < datetime(2016,1,1) or count >= 200: 
                return None
            else:
                get_day_candles_with_main_account(symbol,sma_number,closes,from_date=new_from_date,to_date=to_date,count=count)
        return closes
    except Exception as e:
        print(f'{datetime.now()}:couldnt get sma list for symbol {symbol} due to {e}')
        pass
    finally:
        api_connection.close()
        
        
def first_condition_slope_checks(symbol):
    recommended200 = .02
    recommended20_5 = .1
    try:
        # Get the slope angle of the sma 5 for the last 5 days
        prev_five_days_sma_5 = get_sma_to_usable_value(get_5_days_prev_sma5(symbol))
        prev_four_days_sma_5 = get_sma_to_usable_value(get_4_days_prev_sma5(symbol,prev_five_days_sma_5[1]))
        prev_three_days_sma_5 = get_sma_to_usable_value(get_3_days_prev_sma5(symbol,prev_four_days_sma_5[1]))
        prev_two_days_sma_5 = get_sma_to_usable_value(get_2_days_prev_sma5(symbol,prev_three_days_sma_5[1]))
        prev_sma_5 = get_sma_to_usable_value(get_1_day_prev_sma5(symbol,prev_two_days_sma_5[1]))
        current_sma5 = get_sma_to_usable_value(get_sma5(symbol,prev_sma_5[1]))
        sma_5_slope = get_sma_5_slope([prev_four_days_sma_5[0],current_sma5[0]])
        if sma_5_slope > recommended20_5:
            # Get the slope of sma20 for last five days
            prev_five_days_sma_20 = get_sma_to_usable_value(get_5_days_prev_sma20(symbol))
            prev_four_days_sma_20 = get_sma_to_usable_value(get_4_days_prev_sma20(symbol,prev_five_days_sma_20[1]))
            prev_three_days_sma_20 = get_sma_to_usable_value(get_3_days_prev_sma20(symbol,prev_four_days_sma_20[1]))
            prev_two_days_sma_20 = get_sma_to_usable_value(get_2_days_prev_sma20(symbol,prev_three_days_sma_20[1]))
            prev_sma_20 = get_sma_to_usable_value(get_1_day_prev_sma20(symbol,prev_two_days_sma_20[1]))
            current_sma20 = get_sma_to_usable_value(get_sma20(symbol,prev_sma_20[1]))
            sma_20_slope = get_sma_20_slope([prev_four_days_sma_20[0],current_sma20[0]])
            if sma_20_slope > recommended20_5:
                # Get the slope angle of sma200 for last 5 days
                prev_five_days_sma_200 = get_sma_to_usable_value(get_5_days_prev_sma200(symbol))
                prev_four_days_sma_200 = get_sma_to_usable_value(get_4_days_prev_sma200(symbol,prev_five_days_sma_200[1]))
                prev_three_days_sma_200 = get_sma_to_usable_value(get_3_days_prev_sma200(symbol,prev_four_days_sma_200[1]))
                prev_two_days_sma_200 = get_sma_to_usable_value(get_2_days_prev_sma200(symbol,prev_three_days_sma_200[1]))
                prev_sma_200 = get_sma_to_usable_value(get_1_day_prev_sma200(symbol,prev_two_days_sma_200[1]))
                current_sma200 = get_sma_to_usable_value(get_sma200(symbol,prev_sma_200[1]))
                sma_200_slope = get_sma_20_slope([prev_four_days_sma_200[0],current_sma200[0]])
                if sma_200_slope > recommended200:
                   
                    
                    # Check that current 5 is above current 200
                    cur5_above_cur200 = current_sma5[0] > current_sma200[0]
                    # Check that 20 is above 200 at least
                    sma20_above_sma200 = current_sma20[0] > current_sma200[0]
                    # Check that 20 is above 5
                    sma5_above_sma20 = current_sma20[0] < current_sma5[0]
                    # Check that 5 slope > 20 slope > 200 slope and 5 slope at least .15
                    if sma20_above_sma200 == True and cur5_above_cur200 == True and sma5_above_sma20 == True:
                        return True
                
        return False
        
    except Exception as e:
        print(f"Unable to find slope of sma5 due to {e}")
        pass
    
# Conversion Methods
def get_sma_to_usable_value(method):
    try:
        if len(method) > 1:
            value = method[0]
            if value != None:
                value = float("{:.4f}".format(value))
            return [value,method[1]]
        else:
            value = method
            if value != None:
                value = float("{:.4f}".format(value))
            return value
            
    except Exception as e:
        print(e)
        pass
    
def get_5_days_prev_sma5(position):
    try:
        symbol = position
    except Exception as e:
        symbol = position
            
    finally:
        sma_list = get_sma_list(symbol,10,[],(datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d"),datetime.now().strftime("%Y-%m-%d"))
        sma_list_copy = deepcopy(sma_list)
        if len(sma_list) != None and sma_list != []:
            sma_list.pop()
            sma_list.pop()
            sma_list.pop()
            sma_list.pop()
            sma_list.pop()
            current_sma5 = float(sum(sma_list) / 5)
            return [current_sma5,sma_list_copy]
        
# GET SMA's
def get_sma5(position,sma_list):
    try:
        symbol = position
    except Exception as e:
        symbol = position
            
    finally:
        sma_list_copy = deepcopy(sma_list)
        if sma_list != None and sma_list != [] and None not in sma_list:
            sma_list.pop(0)
            sma_list.pop(0)
            sma_list.pop(0)
            sma_list.pop(0)
            sma_list.pop(0)
            current_sma5 = float(sum(sma_list) / 5)
            return [current_sma5,sma_list_copy]       
def get_1_day_prev_sma5(position,sma_list): 
    try:
        symbol = position
    except Exception as e:
        symbol = position
            
    finally:
        sma_list_copy = deepcopy(sma_list)       
        if sma_list != None and sma_list != []:
            sma_list.pop(0)
            sma_list.pop(0)
            sma_list.pop(0)
            sma_list.pop(0)
            sma_list.pop()
            current_sma5 = float(sum(sma_list) / 5)
            return [current_sma5,sma_list_copy]    
def get_2_days_prev_sma5(position,sma_list):
    try:
        symbol = position
    except Exception as e:
        symbol = position
            
    finally:
        sma_list_copy = deepcopy(sma_list)
        if sma_list != None and sma_list != []:
            sma_list.pop(0)
            sma_list.pop(0)
            sma_list.pop(0)
            sma_list.pop()
            sma_list.pop()
            current_sma5 = float(sum(sma_list) / 5)
            return [current_sma5,sma_list_copy]   
def get_3_days_prev_sma5(position,sma_list):
    try:
        symbol = position
    except Exception as e:
        symbol = position
            
    finally:
        sma_list_copy = deepcopy(sma_list)
        if sma_list != None and sma_list != []:
            sma_list.pop(0)
            sma_list.pop(0)
            sma_list.pop()
            sma_list.pop()
            sma_list.pop()
            current_sma5 = float(sum(sma_list) / 5)
            return [current_sma5,sma_list_copy]  
def get_4_days_prev_sma5(position,sma_list):
    try:
        symbol = position
    except Exception as e:
        symbol = position
            
    finally:
        sma_list_copy = deepcopy(sma_list)
        if len(sma_list) != None and sma_list != []:
            sma_list.pop(0)
            sma_list.pop()
            sma_list.pop()
            sma_list.pop()
            sma_list.pop()
            current_sma5 = float(sum(sma_list) / 5)
            return [current_sma5,sma_list_copy]
def get_5_days_prev_sma5(position):
    try:
        symbol = position
    except Exception as e:
        symbol = position
            
    finally:
        symbol = symbol[0]
        sma_list = get_sma_list(symbol,10,[],(datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d"),datetime.now().strftime("%Y-%m-%d"))
        sma_list_copy = deepcopy(sma_list)
        if len(sma_list) != None and sma_list != []:
            sma_list.pop()
            sma_list.pop()
            sma_list.pop()
            sma_list.pop()
            sma_list.pop()
            current_sma5 = float(sum(sma_list) / 5)
            return [current_sma5,sma_list_copy]

#  SMA 20's 
def get_sma20(position,sma_list):
    try:
        symbol = position
    except Exception as e:
        symbol = position
            
    finally:
        sma_list_copy = deepcopy(sma_list)
        if sma_list != None and sma_list != [] and None not in sma_list:
            sma_list.pop(0)
            sma_list.pop(0)
            sma_list.pop(0)
            sma_list.pop(0)
            sma_list.pop(0)
            current_sma20 = float(sum(sma_list) / 20)
            return [current_sma20,sma_list_copy]       
def get_1_day_prev_sma20(position,sma_list): 
    try:
        symbol = position
    except Exception as e:
        symbol = position
            
    finally:
        sma_list_copy = deepcopy(sma_list)       
        if sma_list != None and sma_list != []:
            sma_list.pop(0)
            sma_list.pop(0)
            sma_list.pop(0)
            sma_list.pop(0)
            sma_list.pop()
            current_sma20 = float(sum(sma_list) / 20)
            return [current_sma20,sma_list_copy]    
def get_2_days_prev_sma20(position,sma_list):
    try:
        symbol = position
    except Exception as e:
        symbol = position
            
    finally:
        sma_list_copy = deepcopy(sma_list)
        if sma_list != None and sma_list != []:
            sma_list.pop(0)
            sma_list.pop(0)
            sma_list.pop(0)
            sma_list.pop()
            sma_list.pop()
            current_sma20 = float(sum(sma_list) / 20)
            return [current_sma20,sma_list_copy]   
def get_3_days_prev_sma20(position,sma_list):
    try:
        symbol = position
    except Exception as e:
        symbol = position
            
    finally:
        sma_list_copy = deepcopy(sma_list)
        if sma_list != None and sma_list != []:
            sma_list.pop(0)
            sma_list.pop(0)
            sma_list.pop()
            sma_list.pop()
            sma_list.pop()
            current_sma20 = float(sum(sma_list) / 20)
            return [current_sma20,sma_list_copy]  
def get_4_days_prev_sma20(position,sma_list):
    try:
        symbol = position
    except Exception as e:
        symbol = position
            
    finally:
        sma_list_copy = deepcopy(sma_list)
        if len(sma_list) != None and sma_list != []:
            sma_list.pop(0)
            sma_list.pop()
            sma_list.pop()
            sma_list.pop()
            sma_list.pop()
            current_sma20 = float(sum(sma_list) / 20)
            return [current_sma20,sma_list_copy]
def get_5_days_prev_sma20(position):
    try:
        symbol = position
    except Exception as e:
        symbol = position
    finally:
        symbol = symbol[0]    
        sma_list = get_sma_list(symbol,25,[],(datetime.now() - timedelta(days=25)).strftime("%Y-%m-%d"),datetime.now().strftime("%Y-%m-%d"))
        sma_list_copy = deepcopy(sma_list)
        if len(sma_list) != None and sma_list != []:
            sma_list.pop()
            sma_list.pop()
            sma_list.pop()
            sma_list.pop()
            sma_list.pop()
            current_sma20 = float(sum(sma_list) / 20)
            return [current_sma20,sma_list_copy] 

# SMA 200 
def get_sma200(position,sma_list):
    try:
        symbol = position
    except Exception as e:
        symbol = position
    finally:
        symbol = symbol[0]   
        sma_list_copy = deepcopy(sma_list)
        if sma_list != None and sma_list != [] and None not in sma_list:
            sma_list.pop(0)
            sma_list.pop(0)
            sma_list.pop(0)
            sma_list.pop(0)
            sma_list.pop(0)
            current_sma200 = float(sum(sma_list) / 200)
            return [current_sma200,sma_list_copy]       
def get_1_day_prev_sma200(position,sma_list): 
    try:
        symbol = position
    except Exception as e:
        symbol = position
            
    finally:
        sma_list_copy = deepcopy(sma_list)       
        if sma_list != None and sma_list != []:
            sma_list.pop(0)
            sma_list.pop(0)
            sma_list.pop(0)
            sma_list.pop(0)
            sma_list.pop()
            current_sma200 = float(sum(sma_list) / 200)
            return [current_sma200,sma_list_copy]    
def get_2_days_prev_sma200(position,sma_list):
    try:
        symbol = position
    except Exception as e:
        symbol = position
            
    finally:
        sma_list_copy = deepcopy(sma_list)
        if sma_list != None and sma_list != []:
            sma_list.pop(0)
            sma_list.pop(0)
            sma_list.pop(0)
            sma_list.pop() 
            sma_list.pop() 
            current_sma200 = float(sum(sma_list) / 200)
            return [current_sma200,sma_list_copy]   
def get_3_days_prev_sma200(position,sma_list):
    try:
        symbol = position
    except Exception as e:
        symbol = position
            
    finally:
        sma_list_copy = deepcopy(sma_list)
        if sma_list != None and sma_list != []:
            sma_list.pop(0)
            sma_list.pop(0)
            sma_list.pop()
            sma_list.pop()
            sma_list.pop()
            current_sma200 = float(sum(sma_list) / 200)
            return [current_sma200,sma_list_copy]  
def get_4_days_prev_sma200(position,sma_list):
    try:
        symbol = position
    except Exception as e:
        symbol = position
            
    finally:
        sma_list_copy = deepcopy(sma_list)
        if len(sma_list) != None and sma_list != []:
            sma_list.pop(0)
            sma_list.pop()
            sma_list.pop()
            sma_list.pop()
            sma_list.pop()
            sma_list

            current_sma200 = float(sum(sma_list) / 200)
            return [current_sma200,sma_list_copy]
def get_5_days_prev_sma200(position):
    try:
        symbol = position
    except Exception as e:
        symbol = position
            
    finally:
        symbol = symbol[0]
        sma_list = get_sma_list(symbol,205,[],(datetime.now() - timedelta(days=205)).strftime("%Y-%m-%d"),datetime.now().strftime("%Y-%m-%d"))
        sma_list_copy = deepcopy(sma_list)
        if len(sma_list) != None and sma_list != []:
            sma_list.pop()
            sma_list.pop()
            sma_list.pop()
            sma_list.pop()
            sma_list.pop()
            current_sma200 = float(sum(sma_list) / 200)
            return [current_sma200,sma_list_copy] 
        
        
def get_sma_20_slope(sma_20_list):
    sma_start_point = sma_20_list[0]
    sma_end_point = sma_20_list[-1]
    sma_20_slope = get_slope_of_line(sma_start_point,sma_end_point,5)
    return sma_20_slope

def get_sma_5_slope(sma_5_list):
    sma_start_point = sma_5_list[0]
    sma_end_point = sma_5_list[-1]
    sma_5_slope = get_slope_of_line(sma_start_point,sma_end_point,5)
    return sma_5_slope

def get_sma_100_slope(sma_100_list):
    sma_start_point = sma_100_list[0]
    sma_end_point = sma_100_list[-1]
    sma_100_slope = get_slope_of_line(sma_start_point,sma_end_point,5)
    return sma_100_slope

def get_slope_of_line(sma_start_point, sma_end_point, sma_number):
    required_slope = .10
    slope = (sma_end_point - sma_start_point) / sma_number
    return slope