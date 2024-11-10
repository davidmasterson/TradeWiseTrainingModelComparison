from database import transactions_DAOIMPL, metrics_DAOIMPL
import json
from datetime import date
from Models import plotters, transaction

def calculate_daily_metrics_values(user_id):
        today = date.today()
        cumulative_correct_predictions = transactions_DAOIMPL.calculate_correct_predictions_for_user(user_id)
        cumulative_incorrect_predictions = transactions_DAOIMPL.calculate_incorrect_predictions_for_user(user_id)
        accuracy = cumulative_correct_predictions / (cumulative_correct_predictions + cumulative_incorrect_predictions)
        error_rate = 1 - accuracy
        time_to_close_correct_predictions = transactions_DAOIMPL.calculate_average_days_to_close_for_user(user_id)
        cumulative_loss_result = transactions_DAOIMPL.calculate_cumulative_loss_for_user(user_id)
        cumulative_profit_result = transactions_DAOIMPL.calculate_cumulative_profit_for_user(user_id)
        if cumulative_profit_result != None:
            if cumulative_profit_result > 0.00:
                cumulative_profit = cumulative_profit_result
        else:
            cumulative_profit = 0.00
        if cumulative_loss_result != None:
            if cumulative_loss_result < 0.00:
                cumulative_loss = cumulative_loss_result
        else:
            cumulative_loss = 0.00
        # cumulative_profit = cumulative_profit_result if cumulative_profit_result != None and cumulative_profit_result > 0.00 else 0.00
        # cumulative_loss = cumulative_loss_result if cumulative_loss_result != None and cumulative_loss_result < 0.00 else 0.00
        sectors_jsons = Metric.get_sector_data_for_trained_model_profit_loss_rec_and_notrec_for_user(user_id)
        sector_breakdown_profit = sectors_jsons[0]
        sector_breakdown_loss = sectors_jsons[1]
        user_id = user_id
        
        metric = Metric(accuracy,error_rate,cumulative_correct_predictions,cumulative_incorrect_predictions,
                        time_to_close_correct_predictions,cumulative_profit,cumulative_loss, sector_breakdown_profit,
                        sector_breakdown_loss,today,user_id)
        return metric

class Metric:

     def __init__(self, accuracy, error_rate, cumulative_correct_predictions, cumulative_incorrect_predictions,
                  time_to_close_correct_predictions, cumulative_profit, cumulative_loss, sector_breakdown_profit,sector_breakdown_loss,
                   date, user_id):
         self.accuracy = accuracy
         self.error_rate = error_rate
         self.cumulative_correct_predictions = cumulative_correct_predictions
         self.cumulative_incorrect_predictions = cumulative_incorrect_predictions
         self.time_to_close_correct_predictions = time_to_close_correct_predictions
         self.cumulative_profit = cumulative_profit
         self.cumulative_loss = cumulative_loss
         self.sector_breakdown_profit = sector_breakdown_profit
         self.sector_breakdown_loss = sector_breakdown_loss
         self.date = date
         self.user_id = user_id


     def plot_model_metrics(user_id):
         metrics_time_frames = metrics_DAOIMPL.get_metrics_dates_by_user(user_id)
         metrics_time_frames = [acc[0] for acc in metrics_time_frames]

         accuracy_values = metrics_DAOIMPL.get_metrics_accuracies_for_user(user_id)
         accuracy_values = [float(acc[0]) for acc in accuracy_values]

         error_rates_values = metrics_DAOIMPL.get_metrics_error_rates_for_user(user_id)
         error_rates_values = [float(acc[0]) for acc in error_rates_values]

         cumulative_correct_predictions_values = metrics_DAOIMPL.get_metrics_cumlative_correct_predictions_for_user(user_id)
         cumulative_correct_predictions_values = [int(acc[0]) for acc in cumulative_correct_predictions_values]

         cumulative_incorrect_predictions_values = metrics_DAOIMPL.get_metrics_cumlative_incorrect_predictions_for_user(user_id)
         cumulative_incorrect_predictions_values = [int(acc[0]) for acc in cumulative_incorrect_predictions_values]

         times_to_close_values = metrics_DAOIMPL.get_metrics_times_to_close_for_user(user_id)
         times_to_close_values = [acc[0] for acc in times_to_close_values]

         cumulative_profits_values = metrics_DAOIMPL.get_metrics_cumlative_profits_for_user(user_id)
         cumulative_profits_values = [float(acc[0]) for acc in cumulative_profits_values]

         cumulative_losses_values = metrics_DAOIMPL.get_metrics_cumlative_losses_for_user(user_id)
         cumulative_losses_values = [float(acc[0]) for acc in cumulative_losses_values]

         plotters.plot_accuracy(accuracy_values, metrics_time_frames, user_id)
         plotters.plot_error_rate(error_rates_values, metrics_time_frames, user_id)
         plotters.plot_cumulative_correct_predictions(cumulative_correct_predictions_values, metrics_time_frames, user_id)
         plotters.plot_cumulative_incorrect_predictions(cumulative_incorrect_predictions_values,metrics_time_frames, user_id)
         plotters.plot_time_to_close(times_to_close_values, user_id)
         plotters.plot_cumulative_profit(cumulative_profits_values, metrics_time_frames, user_id)
         plotters.plot_cumulative_loss(cumulative_losses_values, metrics_time_frames, user_id)
         # Get last breakdown info and plot
         db_breakdowns = metrics_DAOIMPL.get_all_last_sector_breakdowns_for_user(user_id)
         plotters.plot_model_sector_breakdown_profits(db_breakdowns[0], user_id)
         plotters.plot_model_sector_breakdown_loss(db_breakdowns[1], user_id)


     def get_sector_data_for_trained_model_profit_loss_rec_and_notrec_for_user(user_id):
         #profit sectors
         prof_sectors_dict = transactions_DAOIMPL.get_profit_sectors_for_user(user_id)
         prof_sector_json = json.dumps(prof_sectors_dict)

         #loss sectors
         loss_sectors_dict = transactions_DAOIMPL.get_profit_sectors_for_user(user_id)
         loss_sector_json = json.dumps(loss_sectors_dict)
         
         return [prof_sector_json,loss_sector_json]
