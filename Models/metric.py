from database import transactions_DAOIMPL, metrics_DAOIMPL
import json
from datetime import date
from Models import plotters, transaction

def calculate_daily_metrics_values(classification_report,future_df):
        accuracy = classification_report['accuracy']
        error_rate = 1 - accuracy
        total_predictions = sum(classification_report[label]['support'] for label in ['0', '1'])
        cumulative_correct_predictions = transactions_DAOIMPL.calculate_correct_predictions()
        cumulative_incorrect_predictions = transactions_DAOIMPL.calculate_incorrect_predictions()
        todays_buys = classification_report['1']['support']
        todays_dont_buys = classification_report['0']['support']
        time_to_close_correct_predictions = transactions_DAOIMPL.calculate_average_days_to_close()
        cumulative_profit = 0
        cumulative_loss = 0
        cumulative_profit = cumulative_profit if transactions_DAOIMPL.calculate_cumulative_profit() < 0.00 else transactions_DAOIMPL.calculate_cumulative_profit()
        cumulative_loss = cumulative_loss if transactions_DAOIMPL.calculate_cumulative_loss() > 0.00 else transactions_DAOIMPL.calculate_cumulative_loss()
        sector_breakdown = future_df['sector'].value_counts().to_dict()
        sector_breakdown_json = json.dumps(sector_breakdown)
        
        metric = Metric(accuracy,error_rate,cumulative_correct_predictions,cumulative_incorrect_predictions,todays_buys,todays_dont_buys,
                        time_to_close_correct_predictions,cumulative_profit,cumulative_loss, sector_breakdown_json,date.today())
        return metric

class Metric:

    def __init__(self, accuracy, error_rate, cumulative_correct_predictions, cumulative_incorrect_predictions, todays_buys, todays_dont_buys,
                 time_to_close_correct_predictions, cumulative_profit, cumulative_loss, sector_breakdown, date):
        self.accuracy = accuracy
        self.error_rate = error_rate
        self.cumulative_correct_predictions = cumulative_correct_predictions
        self.cumulative_incorrect_predictions = cumulative_incorrect_predictions
        self.todays_buys = todays_buys
        self.todays_dont_buys = todays_dont_buys
        self.time_to_close_correct_predictions = time_to_close_correct_predictions
        self.cumulative_profit = cumulative_profit
        self.cumulative_loss = cumulative_loss
        self.sector_breakdown = sector_breakdown
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
        Metric.plot_sector_breakdown_profit()
        Metric.plot_sector_breakdown_loss()
        Metric.plot_sector_breakdown_recommends()
        Metric.plot_sector_breakdown_non_recommends()

        
    def plot_sector_breakdown_profit():
         symbols = transactions_DAOIMPL.select_model_sector_profits_symbols()
         symbols_dict = transaction.transaction.aggregate_sectors_for_stock_symbols(symbols)
         plotters.plot_model_sector_breakdown_profits(symbols_dict)
    
    def plot_sector_breakdown_loss():
         symbols = transactions_DAOIMPL.select_model_sector_loss_symbols()
         symbols_dict = transaction.transaction.aggregate_sectors_for_stock_symbols(symbols)
         plotters.plot_model_sector_breakdown_loss(symbols_dict)
    
    def plot_sector_breakdown_recommends():
         symbols = transactions_DAOIMPL.select_model_sector_recommended_symbols()
         symbols_dict = transaction.transaction.aggregate_sectors_for_stock_symbols(symbols)
         plotters.plot_model_sector_breakdown_recommend(symbols_dict)
    
    def plot_sector_breakdown_non_recommends():
         symbols = transactions_DAOIMPL.select_model_sector_not_recommended_symbols()
         symbols_dict = transaction.transaction.aggregate_sectors_for_stock_symbols(symbols)
         plotters.plot_model_sector_breakdown_not_recommend(symbols_dict)
         