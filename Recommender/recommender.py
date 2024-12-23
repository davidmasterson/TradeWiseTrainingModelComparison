from Hypothetical_Predictor import CSV_Writer
import logging
from database import  progression_DAOIMPL
from datetime import datetime






def get_model_recommendations_for_recommender(new_list,recommendations_script_id, dataset_id, user_id, 
                                              max_total_spend,recommendation_count,model_id, progression = 20, count=0, iter=0, symbols=None):
    
    
    from Models import progress_object, recommendation_script
    
    import pandas as pd
    
    
    project_root = "/home/ubuntu/TradeWiseTrainingModelComparison"
        
        
    
    if symbols is None:
        symbols = []  # Initialize symbols as an empty list if not provided
        
    try:    
        # Process the stock list in chunks
        while len(symbols) < recommendation_count:
            total_stocks_iter = iter * 50
            progress_text = f'Checking stocks {total_stocks_iter} to {total_stocks_iter + 50} out of  {len(new_list)}'
            try:
                progression_text = progression_DAOIMPL.get_progression_text_by_user(user_id)
                if progression_text:
                    progression_DAOIMPL.update_progression_text(progress_text,user_id,progression_text[0])
                else:
                    progression_DAOIMPL.insert_progression_text(progress_text,user_id)
            except Exception as e:
                logging.info(f' unable to insert progression text due to {e}')
            logging.info(progress_text)
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
                prog_text = progression_DAOIMPL.get_progression_text_by_user(user_id)
                if prog_text:
                    progression_DAOIMPL.update_progression_text('Finished Scanning', user_id,prog_text[0] )
                break

            # Write temporary CSV file with stock data
            csv_ds = CSV_Writer.CSV_Writer.write_temporary_csv(this_iter_list)
            df = pd.read_csv('Hypothetical_Predictor/transactions.csv')

            # Fetch the stock data
            
                


            # Run preprocessing

            # Get predictions from the model
            probs = recommendation_script.RecommendationScript.retrainer_for_recommender(recommendations_script_id,project_root, user_id, dataset_id, model_id)


            # Open the file in append mode after the first iteration
            if probs:
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
            logging.info(progress_text)
            if count > len(new_list):
                logging.info('Finished processing symbols:', symbols)
                return symbols

            
            
        
        logging.info('Finished processing symbols:', symbols)
        return symbols
    except Exception as e:
        logging.exception(f'Recommender has errored out due to {e}')
        prog_text = progression_DAOIMPL.get_progression_text_by_user(user_id)
        if prog_text:
            progression_DAOIMPL.update_progression_text(f'''An error has occured, please contact support with the following info
                                                        {user_id}, {datetime.now()}, {e}''',user_id, prog_text[0] )




