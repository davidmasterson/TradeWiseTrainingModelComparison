import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Finder import symbol_finder
from Recommender import recommender
from Purchaser import score_based_purchaser





assets_list = symbol_finder.get_list_of_tradeable_stocks()
assets_list = symbol_finder.fetch_price_data_concurrently(assets_list)
assets_list = symbol_finder.sort_list_from_lowest_price_to_highest_price(assets_list)
symbols_to_purchase = recommender.get_model_recommendation(assets_list)
score_based_purchaser.process_symbols_for_purchase(symbols_to_purchase, min_spend, max_spend)

