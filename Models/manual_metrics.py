from database import transactions_DAOIMPL, manual_metrics_DAOIMPL
from Models import plotters, transaction
import json
from datetime import date


def calculate_manual_metrics():
     today = date.today()
     cumulative_correct_predictions = Manual_metrics.calculate_manual_algo_cumulative_correct()
     cumulative_incorrect_predictions = Manual_metrics.calculate_manual_algo_cumulative_incorrect()
     accuracy = Manual_metrics.calculate_manual_algo_accuracy_rate()
     inaccurate = Manual_metrics.calculate_manual_algo_inaccuracy_rate()
     time_to_close_correct_predictions = Manual_metrics.calculate_manual_algo_correct_pred_time_to_close()
     cumulative_profit = Manual_metrics.calculate_manual_algo_cumulative_profit()
     cumulative_loss = Manual_metrics.calculate_manual_algo_cumulative_loss()
     sectors_jsons = Manual_metrics.get_sector_data_for_trained_model_profit_loss_rec_and_notrec()
     sector_breakdown_profit = sectors_jsons[0]
     sector_breakdown_loss = sectors_jsons[1]
     sector_breakdown_rec = sectors_jsons[2]


     manual_metric = Manual_metrics(accuracy,inaccurate,cumulative_correct_predictions,cumulative_incorrect_predictions,
                                        time_to_close_correct_predictions,cumulative_profit,cumulative_loss,sector_breakdown_profit,
                                        sector_breakdown_loss,sector_breakdown_rec,today)
    
     return manual_metric


class Manual_metrics:

     def __init__(self, accuracy, error_rate, cumulative_correct_predictions, cumulative_incorrect_predictions,
                  time_to_close_correct_predictions, cumulative_profit, cumulative_loss, sector_breakdown_profit,
                  sector_breakdown_loss,sector_breakdown_rec, date):
         self.accuracy = accuracy
         self.error_rate = error_rate
         self.cumulative_correct_predictions = cumulative_correct_predictions
         self.cumulative_incorrect_predictions = cumulative_incorrect_predictions
         self.time_to_close_correct_predictions = time_to_close_correct_predictions
         self.cumulative_profit = cumulative_profit
         self.cumulative_loss = cumulative_loss
         self.sector_breakdown_profit = sector_breakdown_profit
         self.sector_breakdown_loss = sector_breakdown_loss
         self.sector_breakdown_rec = sector_breakdown_rec
         self.date = date


     def calculate_manual_algo_accuracy_rate():
          correct = Manual_metrics.calculate_manual_algo_cumulative_correct()
          incorrect = Manual_metrics.calculate_manual_algo_cumulative_incorrect()
          accuracy = correct / (correct + incorrect)
          return accuracy
     
     def calculate_manual_algo_inaccuracy_rate():
          accurate = Manual_metrics.calculate_manual_algo_accuracy_rate()
          inaccuracy = 1 - accurate
          return inaccuracy
     
     def calculate_manual_algo_cumulative_correct():
          correct = transactions_DAOIMPL.calculate_manual_algo_correct()
          return correct
     
     def calculate_manual_algo_cumulative_incorrect():
          incorrect = transactions_DAOIMPL.calculate_manual_algo_incorrect()
          return incorrect
     
     def calculate_manual_algo_correct_pred_time_to_close():
          days = transactions_DAOIMPL.calculate_manual_algo_time_to_close_correct_pred()
          return days
     
     def calculate_manual_algo_cumulative_profit():
          profit = transactions_DAOIMPL.calculate_manual_algo_cumulative_profit()
          return profit
     
     def calculate_manual_algo_cumulative_loss():
          loss = transactions_DAOIMPL.calculate_manual_algo_cumulative_loss()
          return loss
    

     def plot_manual_metrics():
          manual_time_frames = manual_metrics_DAOIMPL.get_metrics_dates()
          manual_time_frames = [acc[0] for acc in manual_time_frames]

          manual_accuracys_values = manual_metrics_DAOIMPL.get_manual_metrics_accuracies()
          manual_accuracys_values = [float(acc[0]) for acc in manual_accuracys_values]

          manual_error_rates_values = manual_metrics_DAOIMPL.get_manual_metrics_error_rates()
          manual_error_rates_values = [float(acc[0]) for acc in manual_error_rates_values]

          manual_cumulative_correct_predictions_values = manual_metrics_DAOIMPL.get_manual_metrics_cumlative_correct_predictions()
          manual_cumulative_correct_predictions_values = [int(acc[0]) for acc in manual_cumulative_correct_predictions_values]

          manual_cumulative_incorrect_predictions_values = manual_metrics_DAOIMPL.get_manual_metrics_cumlative_incorrect_predictions()
          manual_cumulative_incorrect_predictions_values = [int(acc[0]) for acc in manual_cumulative_incorrect_predictions_values]

          manual_times_to_close_values = manual_metrics_DAOIMPL.get_manual_metrics_times_to_close()
          manual_times_to_close_values = [int(acc[0]) for acc in manual_times_to_close_values]

          manual_cumulative_profits_values = manual_metrics_DAOIMPL.get_manual_metrics_cumlative_profits()
          manual_cumulative_profits_values = [float(acc[0]) for acc in manual_cumulative_profits_values]

          manual_cumulative_losses_values = manual_metrics_DAOIMPL.get_manual_metrics_cumlative_losses()
          manual_cumulative_losses_values = [float(acc[0]) for acc in manual_cumulative_losses_values]

          plotters.plot_manual_accuracy(manual_accuracys_values,manual_time_frames)
          plotters.plot_manual_error_rate(manual_error_rates_values, manual_time_frames)
          plotters.plot_manual_cumulative_correct_predictions(manual_cumulative_correct_predictions_values, manual_time_frames)
          plotters.plot_manual_cumulative_incorrect_predictions(manual_cumulative_incorrect_predictions_values, manual_time_frames)
          plotters.plot_manual_time_to_close(manual_times_to_close_values)
          plotters.plot_manual_cumulative_profit(manual_cumulative_profits_values, manual_time_frames)
          plotters.plot_manual_cumulative_loss(manual_cumulative_losses_values, manual_time_frames)
          # Get last breakdown info and plot
          db_breakdowns = manual_metrics_DAOIMPL.get_all_last_sector_breakdowns()
          plotters.plot_manual_sector_breakdown_profits(db_breakdowns[0])
          plotters.plot_manual_sector_breakdown_loss(db_breakdowns[1])
          plotters.plot_manual_sector_breakdown_recommend(db_breakdowns[2])
          
        
        

        
     def get_sector_data_for_trained_model_profit_loss_rec_and_notrec():
         #profit sectors
         prof_symbols = transactions_DAOIMPL.select_manual_sector_profits_symbols()
         prof_symbols_dict = transaction.transaction.aggregate_sectors_for_stock_symbols(prof_symbols)
         prof_sector_json = json.dumps(prof_symbols_dict)

         #loss sectors
         loss_symbols = transactions_DAOIMPL.select_manual_sector_loss_symbols()
         loss_symbols_dict = transaction.transaction.aggregate_sectors_for_stock_symbols(loss_symbols)
         loss_sector_json = json.dumps(loss_symbols_dict)
         #recommended sectors
         rec_symbols = transactions_DAOIMPL.select_manual_sector_recommended_symbols()
         rec_sybols_dict = transaction.transaction.aggregate_sectors_for_stock_symbols(rec_symbols)
         rec_sectors_json = json.dumps(rec_sybols_dict)
         return [prof_sector_json,loss_sector_json,rec_sectors_json]
     
     
          

          