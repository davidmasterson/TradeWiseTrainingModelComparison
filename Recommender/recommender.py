from Hypothetical_Predictor import CSV_Writer, stock_data_fetcher, predict_with_pre_trained_model
import subprocess
import logging
from database import models_DAOIMPL, progression_DAOIMPL
from MachineLearningModels import manual_alg_requisition_script


def get_model_recommendation(stock_list, count=0, iter=0, symbols=None, max_symbols=10):
    
    if symbols is None:
        
        symbols = []  # Initialize symbols as an empty list if not provided
        
    # Process the stock list in chunks
    while len(symbols) < max_symbols:
       
        # Get the current chunk (50 stocks at a time)
        this_iter_list = stock_list[iter * 50: (iter + 1) * 50]
        if not this_iter_list:  # Exit if no more stocks are left
            break

        # Write temporary CSV file with stock data
        # CSV_Writer.CSV_Writer.write_temporary_csv(this_iter_list)

        # Fetch the stock data
        
              


        # Run preprocessing

        # Get predictions from the model
        probs = manual_alg_requisition_script.get_positions_to_buy(this_iter_list)


        # Open the file in append mode after the first iteration
        
        for prob in probs:
            # Check if the prediction meets the condition (prob[-1] == 1)
            
            symbols.append(prob)  # Append the symbol to the list
            if len(symbols) >= max_symbols:  # Stop when we have enough symbols
                logging.info(symbols)
                return symbols

        # Update iteration and count for the next loop
        iter += 1
        count += 50
        progress_now = 50 + (4 * len(symbols))
        progress = progression_DAOIMPL.get_recommender_progress()
        progression_DAOIMPL.update_recommender_progress(progress_now,progress[0])

    logging.info('Finished processing symbols:', symbols)
    return symbols




