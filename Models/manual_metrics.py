from database import transactions_DAOIMPL, manual_metrics_DAOIMPL
from Models import plotters, transaction
import json


def calculate_manual_metrics(sector_breakdown):
     from datetime import date
     today = date.today()
     accuracy = Manual_metrics.calculate_manual_algo_accuracy_rate()
     inaccurate = Manual_metrics.calculate_manual_algo_inaccuracy_rate()
     cumulative_correct_predictions = Manual_metrics.calculate_manual_algo_cumulative_correct()
     cumulative_incorrect_predictions = Manual_metrics.calculate_manual_algo_cumulative_incorrect()
     todays_buys = Manual_metrics.get_todays_manual_algo_buys(today)
     time_to_close_correct_predictions = Manual_metrics.calculate_manual_algo_correct_pred_time_to_close()
     cumulative_profit = Manual_metrics.calculate_manual_algo_cumulative_profit()
     cumulative_loss = Manual_metrics.calculate_manual_algo_cumulative_loss()
     sector_breakdown = sector_breakdown
     date = date.today()

     manual_metric = Manual_metrics(accuracy,inaccurate,cumulative_correct_predictions,cumulative_incorrect_predictions,todays_buys,
                                        time_to_close_correct_predictions,cumulative_profit,cumulative_loss,sector_breakdown,date)
    
     return manual_metric


class Manual_metrics:

     def __init__(self, accuracy, error_rate, cumulative_correct_predictions, cumulative_incorrect_predictions, todays_buys,
                  time_to_close_correct_predictions, cumulative_profit, cumulative_loss, sector_breakdown, date):
         self.accuracy = accuracy
         self.error_rate = error_rate
         self.cumulative_correct_predictions = cumulative_correct_predictions
         self.cumulative_incorrect_predictions = cumulative_incorrect_predictions
         self.todays_buys = todays_buys
         self.time_to_close_correct_predictions = time_to_close_correct_predictions
         self.cumulative_profit = cumulative_profit
         self.cumulative_loss = cumulative_loss
         self.sector_breakdown = sector_breakdown
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
    
     def get_todays_manual_algo_buys(date):
        date = date.strftime('%Y-%m-%d')
        count = transactions_DAOIMPL.get_todays_manual_algo_buys(date)
        return count
    

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
        Manual_metrics.plot_sector_breakdown_profit()
        Manual_metrics.plot_sector_breakdown_loss()
        Manual_metrics.plot_sector_breakdown_recommends()
        

        
     def plot_sector_breakdown_profit():
          symbols = transactions_DAOIMPL.select_manual_sector_profits_symbols()
          symbols_dict = transaction.transaction.aggregate_sectors_for_stock_symbols(symbols)
          plotters.plot_manual_sector_breakdown_profits(symbols_dict)
     
     def plot_sector_breakdown_loss():
          symbols = transactions_DAOIMPL.select_manual_sector_loss_symbols()
          symbols_dict = transaction.transaction.aggregate_sectors_for_stock_symbols(symbols)
          plotters.plot_manual_sector_breakdown_loss(symbols_dict)
     
     def plot_sector_breakdown_recommends():
          symbols = transactions_DAOIMPL.select_manual_sector_recommended_symbols()
          symbols_dict = transaction.transaction.aggregate_sectors_for_stock_symbols(symbols)
          plotters.plot_manual_sector_breakdown_recommend(symbols_dict)
     
     
          

          