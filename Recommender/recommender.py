from Hypothetical_Predictor import CSV_Writer, stock_data_fetcher, predict_with_pre_trained_model
import subprocess
import logging
from database import models_DAOIMPL, progression_DAOIMPL
from MachineLearningModels import manual_alg_requisition_script




# def get_model_recommendation(stock_list, count=0, iter=0, symbols=None, max_symbols=20):
    
#     if symbols is None:
        
#         symbols = []  # Initialize symbols as an empty list if not provided
        
#     # Process the stock list in chunks
#     while len(symbols) < max_symbols:
       
#         # Get the current chunk (50 stocks at a time)
#         this_iter_list = stock_list[iter * 50: (iter + 1) * 50]
#         if not this_iter_list:  # Exit if no more stocks are left
#             break

#         # Write temporary CSV file with stock data
#         # CSV_Writer.CSV_Writer.write_temporary_csv(this_iter_list)

#         # Fetch the stock data
        
              


#         # Run preprocessing

#         # Get predictions from the model
#         probs = manual_alg_requisition_script.get_positions_to_buy(this_iter_list)


#         # Open the file in append mode after the first iteration
        
#         for prob in probs:
#             # Check if the prediction meets the condition (prob[-1] == 1)
            
#             symbols.append(prob)  # Append the symbol to the list
#             if len(symbols) >= max_symbols:  # Stop when we have enough symbols
#                 logging.info(symbols)
#                 return symbols

#         # Update iteration and count for the next loop
#         iter += 1
#         count += 50
#         progress_now = 50 + (2 * len(symbols))
#         progress = progression_DAOIMPL.get_recommender_progress_by_user(user_id)
#         progression_DAOIMPL.update_recommender_progress(progress_now,progress[0])

#     logging.info('Finished processing symbols:', symbols)
#     return symbols


def get_model_recommendations_for_recommender(new_list,preprocessing_script_id, model_name, model_id, user_id, 
                                              max_total_spend,recommendation_count, progression = 20, count=0, iter=0, symbols=None):
    from MachineLearningModels import MARecommender
    from Models import progress_object
    if symbols is None:
        
        
        
        
        
        
        
        
        symbols = []  # Initialize symbols as an empty list if not provided
        
        
    # Process the stock list in chunks
    while len(symbols) < recommendation_count:
        progress_now = len(symbols) * (100 - progression) / recommendation_count
        current_progress = progression_DAOIMPL.get_recommender_progress_by_user(user_id)
        if current_progress:
            progression_DAOIMPL.update_recommender_progress(progress_now, user_id, int(current_progress[0]))
        else:
            new_progress = progress_object.Progress(progress_now, user_id)
            progression_DAOIMPL.insert_recommender_progress(new_progress)
       
        # Get the current chunk (50 stocks at a time)
        this_iter_list = new_list[iter * 50: (iter + 1) * 50]
        if not this_iter_list:  # Exit if no more stocks are left
            break

        # Write temporary CSV file with stock data
        CSV_Writer.CSV_Writer.write_temporary_csv(this_iter_list)

        # Fetch the stock data
        
              


        # Run preprocessing

        # Get predictions from the model
        probs = MARecommender.preprocess_data(user_id, model_name)


        # Open the file in append mode after the first iteration
        
        for prob in probs:
            # Check if the prediction meets the condition (prob[-1] == 1)
            
            symbols.append(prob)  # Append the symbol to the list
            if len(symbols) >= recommendation_count:  # Stop when we have enough symbols
                logging.info(symbols)
                progress_now = len(symbols) * (100 - progression) / recommendation_count
                progress = progression_DAOIMPL.get_recommender_progress_by_user(user_id)
                progression_DAOIMPL.update_recommender_progress(progress_now,user_id,progress[0])
                return symbols
        logging.error(f'{symbols}')
        # Update iteration and count for the next loop
        iter += 1
        count += 50
        

    logging.info('Finished processing symbols:', symbols)
    return symbols




