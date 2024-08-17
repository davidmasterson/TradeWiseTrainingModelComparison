import alpaca_request_methods
from database import transactions_DAOIMPL

trans = alpaca_request_methods.fetch_stock_data()
print(trans)