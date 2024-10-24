import ast
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Finder import symbol_finder
from Recommender import recommender
from Purchaser import score_based_purchaser
from Models import user
from database import trade_settings_DAOIMPL, progression_DAOIMPL
from flask import session
from MachineLearningModels import manual_alg_requisition_script
import sector_finder


def generate_recommendations_task(user_id):
    user_id = user.User.get_id()
    
    user_preferences = trade_settings_DAOIMPL.get_trade_settings_by_user(user_id)
    min_spend = user_preferences[2]
    max_spend = user_preferences[3]
    max_total_spend = user_preferences[7]
    
    # Get and Set progress for /progress route to send to frontend
    
    
    
    get_and_set_progress(0)
    assets_list = symbol_finder.get_list_of_tradeable_stocks()
    assets_list = symbol_finder.fetch_price_data_concurrently(assets_list,min_spend,max_spend)
    get_and_set_progress(50)
    assets_list = symbol_finder.sort_list_from_lowest_price_to_highest_price(assets_list)
    assets_list = str(assets_list)
    assets_list = ast.literal_eval(assets_list)
    
    
    symbols_to_purchase = recommender.get_model_recommendation(assets_list)
    get_and_set_progress(90)
    scores = score_based_purchaser.process_symbols_for_purchase(symbols_to_purchase,max_total_spend)
    final_scores = []
    for score in scores:
        company_name = sector_finder.get_stock_company_name(scores[score]['symbol'])
        info = manual_alg_requisition_script.request_articles(score, company_name)
        sentiment_score = manual_alg_requisition_script.process_phrase_for_sentiment(info,company_name)
        sentiment_score = round(sentiment_score, 2)
        scores[score]['sentiment'] += sentiment_score 
        if scores[score]['sentiment'] >= trade_settings_DAOIMPL.get_trade_settings_by_user(user_id)[5]:
            final_scores.append(scores[score])
        
         
    get_and_set_progress(100)
    return final_scores

def get_and_set_progress(prog_percent):
    prog_id = progression_DAOIMPL.get_recommender_progress()
    if not type(prog_id) == bool and prog_id[1] > -1:
        progression_DAOIMPL.update_recommender_progress(prog_percent,prog_id[0])
    else:
        progression_DAOIMPL.insert_recommender_progress(0)
        



    

