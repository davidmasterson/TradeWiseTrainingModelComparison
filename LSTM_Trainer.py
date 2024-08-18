import alpaca_request_methods
from database import transactions_DAOIMPL
import subprocess

alpaca_request_methods.fetch_stock_data()
model_and_report = subprocess.run(['python', 'model_generator.py'],capture_output=True)

