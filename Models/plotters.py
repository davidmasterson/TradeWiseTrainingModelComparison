import matplotlib.pyplot as plt
import json
import logging

def plot_accuracy(accuracy_values, time_periods):
    # Convert datetime.date objects to strings in 'YYYY-MM-DD' format
    time_periods_str = [date.strftime('%Y-%m-%d') for date in time_periods]
    plt.figure(figsize=(8,5))
    plt.bar(time_periods_str, accuracy_values)
    logging.info(accuracy_values)
    plt.title('Model Accuracy')
    plt.xlabel('Time Period')
    plt.ylabel('Accuracy (%)')
    plt.savefig('static/plots/model_accuracy.png')

def plot_error_rate(error_rate_values, time_periods):
    # Convert datetime.date objects to strings in 'YYYY-MM-DD' format
    time_periods_str = [date.strftime('%Y-%m-%d') for date in time_periods]
    plt.figure(figsize=(8,5))
    plt.bar(time_periods_str, error_rate_values, color='red')
    plt.title('Model Error Rate')
    plt.xlabel('Time Period')
    plt.ylabel('Error Rate (%)')
    plt.savefig('static/plots/model_error_rate.png')

def plot_cumulative_correct_predictions(correct_predictions, time_periods):
    # Convert datetime.date objects to strings in 'YYYY-MM-DD' format
    time_periods_str = [date.strftime('%Y-%m-%d') for date in time_periods]
    plt.figure(figsize=(8,5))
    plt.plot(time_periods_str, correct_predictions, marker='o')
    # plt.fill_between(time_periods, correct_predictions, alpha=0.3)
    plt.title('Cumulative Correct Predictions')
    plt.xlabel('Time Period')
    plt.ylabel('Cumulative Correct Predictions')
    plt.savefig('static/plots/model_cumulative_correct_predictions.png')

def plot_cumulative_incorrect_predictions(incorrect_predictions, time_periods):
    # Convert datetime.date objects to strings in 'YYYY-MM-DD' format
    time_periods_str = [date.strftime('%Y-%m-%d') for date in time_periods]
    plt.figure(figsize=(8,5))
    plt.plot(time_periods_str, incorrect_predictions, marker='o')
    # plt.fill_between(time_periods, incorrect_predictions, alpha=0.3)
    plt.title('Cumulative Incorrect Predictions')
    plt.xlabel('Time Period')
    plt.ylabel('Cumulative Incorrect Predictions')
    plt.savefig('static/plots/model_cumulative_incorrect_predictions.png')

def plot_time_to_close(correct_close_times):
    plt.figure(figsize=(8,5))
    plt.hist(correct_close_times, bins=10, color='green', alpha=0.7)
    plt.title('Time to Close Correct Predictions')
    plt.xlabel('Days to Close')
    plt.ylabel('Frequency')
    plt.savefig('static/plots/model_time_to_close_correct.png')

def plot_cumulative_profit(profit_values, time_periods):
    # Convert datetime.date objects to strings in 'YYYY-MM-DD' format
    time_periods_str = [date.strftime('%Y-%m-%d') for date in time_periods]
    plt.figure(figsize=(8,5))
    plt.plot(time_periods_str, profit_values, marker='o', color='green')
    plt.title('Cumulative Profit')
    plt.xlabel('Time Period')
    plt.ylabel('Cumulative Profit ($)')
    plt.savefig('static/plots/model_cumulative_profit.png')

def plot_cumulative_loss(loss_values, time_periods):
    # Convert datetime.date objects to strings in 'YYYY-MM-DD' format
    time_periods_str = [date.strftime('%Y-%m-%d') for date in time_periods]
    plt.figure(figsize=(8,5))
    plt.plot(time_periods_str, loss_values, marker='o', color='red')
    plt.title('Cumulative Loss')
    plt.xlabel('Time Period')
    plt.ylabel('Cumulative Loss ($)')
    plt.savefig('static/plots/model_cumulative_loss.png')

def plot_model_sector_breakdown_profits(sector_data):
    sector_data = json.loads(sector_data)
    sectors = list(sector_data.keys())
    counts = list(sector_data.values())
    plt.figure(figsize=(8,5))
    plt.pie(counts, labels=sectors, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.title('Sector Breakdown Profits')
    plt.savefig('static/plots/model_sector_breakdown_profits.png')

def plot_model_sector_breakdown_loss(sector_data):
    sector_data = json.loads(sector_data)
    sectors = list(sector_data.keys())
    counts = list(sector_data.values())
    plt.figure(figsize=(8,5))
    plt.pie(counts, labels=sectors, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.title('Sector Breakdown Loss')
    plt.savefig('static/plots/model_sector_breakdown_loss.png')

def plot_model_sector_breakdown_recommend(sector_data):
    sector_data = json.loads(sector_data)
    sectors = list(sector_data.keys())
    counts = list(sector_data.values())
    plt.figure(figsize=(8,5))
    plt.pie(counts, labels=sectors, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.title('Sector Breakdown Recommend')
    plt.savefig('static/plots/model_sector_breakdown_recommend.png')

def plot_model_sector_breakdown_not_recommend(sector_data):
    sector_data = json.loads(sector_data)
    sectors = list(sector_data.keys())
    counts = list(sector_data.values())
    plt.figure(figsize=(8,5))
    plt.pie(counts, labels=sectors, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.title('Sector Breakdown Not Recommended')
    plt.savefig('static/plots/model_sector_breakdown_not_recommend.png')



# Manual algo plots
def plot_manual_accuracy(accuracy_values, time_periods):
    # Convert datetime.date objects to strings in 'YYYY-MM-DD' format
    time_periods_str = [date.strftime('%Y-%m-%d') for date in time_periods]
    plt.figure(figsize=(8,5))
    plt.bar(time_periods_str, accuracy_values)
    plt.title('Model Accuracy')
    plt.xlabel('Time Period')
    plt.ylabel('Accuracy (%)')
    plt.savefig('static/plots/manual_model_accuracy.png')

def plot_manual_error_rate(error_rate_values, time_periods):
    # Convert datetime.date objects to strings in 'YYYY-MM-DD' format
    time_periods_str = [date.strftime('%Y-%m-%d') for date in time_periods]
    plt.figure(figsize=(8,5))
    plt.bar(time_periods_str, error_rate_values, color='red')
    plt.title('Model Error Rate')
    plt.xlabel('Time Period')
    plt.ylabel('Error Rate (%)')
    plt.savefig('static/plots/manual_model_error_rate.png')

def plot_manual_cumulative_correct_predictions(correct_predictions, time_periods):
    # Convert datetime.date objects to strings in 'YYYY-MM-DD' format
    time_periods_str = [date.strftime('%Y-%m-%d') for date in time_periods]
    plt.figure(figsize=(8,5))
    plt.plot(time_periods_str, correct_predictions, marker='o')
    # plt.fill_between(time_periods, correct_predictions, alpha=0.3)
    plt.title('Cumulative Correct Predictions')
    plt.xlabel('Time Period')
    plt.ylabel('Cumulative Correct Predictions')
    plt.savefig('static/plots/manual_model_cumulative_correct_predictions.png')

def plot_manual_cumulative_incorrect_predictions(incorrect_predictions, time_periods):
    # Convert datetime.date objects to strings in 'YYYY-MM-DD' format
    time_periods_str = [date.strftime('%Y-%m-%d') for date in time_periods]
    plt.figure(figsize=(8,5))
    plt.plot(time_periods_str, incorrect_predictions, marker='o')
    # plt.fill_between(time_periods, incorrect_predictions, alpha=0.3)
    plt.title('Cumulative Incorrect Predictions')
    plt.xlabel('Time Period')
    plt.ylabel('Cumulative Incorrect Predictions')
    plt.savefig('static/plots/manual_model_cumulative_incorrect_predictions.png')

def plot_manual_time_to_close(correct_close_times):
    plt.figure(figsize=(8,5))
    plt.hist(correct_close_times, bins=10, color='green', alpha=0.7)
    plt.title('Time to Close Correct Predictions')
    plt.xlabel('Days to Close')
    plt.ylabel('Frequency')
    plt.savefig('static/plots/manual_model_time_to_close_correct.png')

def plot_manual_cumulative_profit(profit_values, time_periods):
    # Convert datetime.date objects to strings in 'YYYY-MM-DD' format
    time_periods_str = [date.strftime('%Y-%m-%d') for date in time_periods]
    plt.figure(figsize=(8,5))
    plt.plot(time_periods_str, profit_values, marker='o', color='green')
    plt.title('Cumulative Profit')
    plt.xlabel('Time Period')
    plt.ylabel('Cumulative Profit ($)')
    plt.savefig('static/plots/manual_model_cumulative_profit.png')

def plot_manual_cumulative_loss(loss_values, time_periods):
    # Convert datetime.date objects to strings in 'YYYY-MM-DD' format
    time_periods_str = [date.strftime('%Y-%m-%d') for date in time_periods]
    plt.figure(figsize=(8,5))
    plt.plot(time_periods_str, loss_values, marker='o', color='red')
    plt.title('Cumulative Loss')
    plt.xlabel('Time Period')
    plt.ylabel('Cumulative Loss ($)')
    plt.savefig('static/plots/manual_model_cumulative_loss.png')

def plot_manual_sector_breakdown_profits(sector_data):
    sector_data = json.loads(sector_data)
    sectors = list(sector_data.keys())
    counts = list(sector_data.values())
    plt.figure(figsize=(8,5))
    plt.pie(counts, labels=sectors, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.title('Sector Breakdown Profits')
    plt.savefig('static/plots/manual_sector_breakdown_profits.png')

def plot_manual_sector_breakdown_loss(sector_data):
    sector_data = json.loads(sector_data)
    sectors = list(sector_data.keys())
    counts = list(sector_data.values())
    plt.figure(figsize=(8,5))
    plt.pie(counts, labels=sectors, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.title('Sector Breakdown Loss')
    plt.savefig('static/plots/manual_sector_breakdown_loss.png')

def plot_manual_sector_breakdown_recommend(sector_data):
    sector_data = json.loads(sector_data)
    sectors = list(sector_data.keys())
    counts = list(sector_data.values())
    plt.figure(figsize=(8,5))
    plt.pie(counts, labels=sectors, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.title('Sector Breakdown Recommend')
    plt.savefig('static/plots/manual_sector_breakdown_recommend.png')
    
    
    
import plotly.graph_objs as go

def generate_model_performance_graph(model_scores):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=model_scores['dates'], y=model_scores['accuracy'],
                             mode='lines', name='Accuracy'))
    fig.add_trace(go.Scatter(x=model_scores['dates'], y=model_scores['precision'],
                             mode='lines', name='Precision'))
    fig.add_trace(go.Scatter(x=model_scores['dates'], y=model_scores['recall'],
                             mode='lines', name='Recall'))

    fig.update_layout(title='Model Performance Over Time',
                      xaxis_title='Date',
                      yaxis_title='Score')

    return fig.to_html()  # To embed in your webpage