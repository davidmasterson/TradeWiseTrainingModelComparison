from database import transactions_DAOIMPL, metrics_DAOIMPL
import json
from datetime import date
from Models import plotters, transaction

def calculate_daily_metrics_values():
        today = date.today()
        cumulative_correct_predictions = transactions_DAOIMPL.calculate_correct_predictions()
        cumulative_incorrect_predictions = transactions_DAOIMPL.calculate_incorrect_predictions()
        accuracy = cumulative_correct_predictions / (cumulative_correct_predictions + cumulative_incorrect_predictions)
        error_rate = 1 - accuracy
        time_to_close_correct_predictions = transactions_DAOIMPL.calculate_average_days_to_close()
        cumulative_profit = 0
        cumulative_loss = 0
        cumulative_profit = cumulative_profit if transactions_DAOIMPL.calculate_cumulative_profit() < 0.00 else transactions_DAOIMPL.calculate_cumulative_profit()
        cumulative_loss = cumulative_loss if transactions_DAOIMPL.calculate_cumulative_loss() > 0.00 else transactions_DAOIMPL.calculate_cumulative_loss()
        sectors_jsons = Metric.get_sector_data_for_trained_model_profit_loss_rec_and_notrec()
        sector_breakdown_profit = sectors_jsons[0]
        sector_breakdown_loss = sectors_jsons[1]
        sector_breakdown_rec = sectors_jsons[2]
        sector_breakdown_nrec = sectors_jsons[3]
        
        metric = Metric(accuracy,error_rate,cumulative_correct_predictions,cumulative_incorrect_predictions,
                        time_to_close_correct_predictions,cumulative_profit,cumulative_loss, sector_breakdown_profit,
                        sector_breakdown_loss,sector_breakdown_rec,sector_breakdown_nrec,today)
        return metric

class Metric:

     def __init__(self, accuracy, error_rate, cumulative_correct_predictions, cumulative_incorrect_predictions,
                  time_to_close_correct_predictions, cumulative_profit, cumulative_loss, sector_breakdown_profit,sector_breakdown_loss,
                  sector_breakdown_rec, sector_breakdown_nrec, date):
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
         self.sector_breakdown_nrec = sector_breakdown_nrec
         self.date = date


     def plot_model_metrics():
         metrics_time_frames = metrics_DAOIMPL.get_metrics_dates()
         metrics_time_frames = [acc[0] for acc in metrics_time_frames]

         accuracy_values = metrics_DAOIMPL.get_metrics_accuracies()
         accuracy_values = [float(acc[0]) for acc in accuracy_values]

         error_rates_values = metrics_DAOIMPL.get_metrics_error_rates()
         error_rates_values = [float(acc[0]) for acc in error_rates_values]

         cumulative_correct_predictions_values = metrics_DAOIMPL.get_metrics_cumlative_correct_predictions()
         cumulative_correct_predictions_values = [int(acc[0]) for acc in cumulative_correct_predictions_values]

         cumulative_incorrect_predictions_values = metrics_DAOIMPL.get_metrics_cumlative_incorrect_predictions()
         cumulative_incorrect_predictions_values = [int(acc[0]) for acc in cumulative_incorrect_predictions_values]

         times_to_close_values = metrics_DAOIMPL.get_metrics_times_to_close()
         times_to_close_values = [int(acc[0]) for acc in times_to_close_values]

         cumulative_profits_values = metrics_DAOIMPL.get_metrics_cumlative_profits()
         cumulative_profits_values = [float(acc[0]) for acc in cumulative_profits_values]

         cumulative_losses_values = metrics_DAOIMPL.get_metrics_cumlative_losses()
         cumulative_losses_values = [float(acc[0]) for acc in cumulative_losses_values]

         plotters.plot_accuracy(accuracy_values, metrics_time_frames)
         plotters.plot_error_rate(error_rates_values, metrics_time_frames)
         plotters.plot_cumulative_correct_predictions(cumulative_correct_predictions_values, metrics_time_frames)
         plotters.plot_cumulative_incorrect_predictions(cumulative_incorrect_predictions_values,metrics_time_frames)
         plotters.plot_time_to_close(times_to_close_values)
         plotters.plot_cumulative_profit(cumulative_profits_values, metrics_time_frames)
         plotters.plot_cumulative_loss(cumulative_losses_values, metrics_time_frames)
         # Get last breakdown info and plot
         db_breakdowns = metrics_DAOIMPL.get_all_last_sector_breakdowns()
         plotters.plot_model_sector_breakdown_profits(db_breakdowns[0])
         plotters.plot_model_sector_breakdown_loss(db_breakdowns[1])
         plotters.plot_model_sector_breakdown_recommend(db_breakdowns[2])
         plotters.plot_model_sector_breakdown_not_recommend(db_breakdowns[3])


     def get_sector_data_for_trained_model_profit_loss_rec_and_notrec():
         #profit sectors
         prof_symbols = transactions_DAOIMPL.select_model_sector_profits_symbols()
         prof_symbols_dict = transaction.transaction.aggregate_sectors_for_stock_symbols(prof_symbols)
         prof_sector_json = json.dumps(prof_symbols_dict)

         #loss sectors
         loss_symbols = transactions_DAOIMPL.select_model_sector_loss_symbols()
         loss_symbols_dict = transaction.transaction.aggregate_sectors_for_stock_symbols(loss_symbols)
         loss_sector_json = json.dumps(loss_symbols_dict)
         #recommended sectors
         rec_symbols = transactions_DAOIMPL.select_model_sector_recommended_symbols()
         rec_sybols_dict = transaction.transaction.aggregate_sectors_for_stock_symbols(rec_symbols)
         rec_sectors_json = json.dumps(rec_sybols_dict)
         #not recommended sectors
         nrec_symbols = transactions_DAOIMPL.select_model_sector_not_recommended_symbols()
         nrec_symbols_dict = transaction.transaction.aggregate_sectors_for_stock_symbols(nrec_symbols)
         nrec_sectors_json = json.dumps(nrec_symbols_dict) 
         return [prof_sector_json,loss_sector_json,rec_sectors_json,nrec_sectors_json]
