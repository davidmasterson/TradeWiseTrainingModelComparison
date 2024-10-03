import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Finder import symbol_finder
from Recommender import recommender
from Purchaser import score_based_purchaser
from database import user_DAOIMPL, user_preferences_DAOIMPL


def generate_recommendations_task(user_id):
    user = user_DAOIMPL.get_user_by_username(user_id)[0]
    user_preferences = user_preferences_DAOIMPL.get_user_preferences(user['id'])
    min_spend = user_preferences[1]
    max_spend = user_preferences[2]
    min_total_spend = user_preferences[3]
    max_total_spend = user_preferences[4]
    
    assets_list = symbol_finder.get_list_of_tradeable_stocks()
    assets_list = symbol_finder.fetch_price_data_concurrently(assets_list,min_spend,max_spend)
    assets_list = symbol_finder.sort_list_from_lowest_price_to_highest_price(assets_list)
    symbols_to_purchase = recommender.get_model_recommendation(assets_list)
    scores = score_based_purchaser.process_symbols_for_purchase(symbols_to_purchase, min_spend, max_spend, min_total_spend, max_total_spend, user_id)
    
    return scores