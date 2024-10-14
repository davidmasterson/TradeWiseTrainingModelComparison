import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Finder import symbol_finder
from Recommender import recommender
from Purchaser import score_based_purchaser
from Models import user
from database import trade_settings_DAOIMPL


def generate_recommendations_task(user_id):
    user_id = user.User.get_id()
    user_preferences = trade_settings_DAOIMPL.get_trade_settings_by_user(user_id)
    min_spend = user_preferences[2]
    max_spend = user_preferences[3]
    min_total_spend = user_preferences[6]
    max_total_spend = user_preferences[7]
    
    assets_list = symbol_finder.get_list_of_tradeable_stocks()
    assets_list = symbol_finder.fetch_price_data_concurrently(assets_list,min_spend,max_spend)
    assets_list = symbol_finder.sort_list_from_lowest_price_to_highest_price(assets_list)
    symbols_to_purchase = recommender.get_model_recommendation(assets_list)
    scores = score_based_purchaser.process_symbols_for_purchase(symbols_to_purchase, min_spend, max_spend, min_total_spend, max_total_spend, user_id)
    
    return scores