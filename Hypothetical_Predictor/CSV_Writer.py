
from datetime import date
import alpaca_request_methods

class CSV_Writer:

    def write_temporary_csv(symbols):
        with open('Hypothetical_Predictor/transactions.csv', 'w') as temporary_writer:
            temporary_writer.write(f'transaction_id,symbol,date_purchased,purchased_pps,qty,total_buy_price,purchase_string,date_sold,sold_pps,total_sell_price,sell_string,expected_return,percentage_roi,actual_return,stop_loss_price,tp1,tp2,sop\n')
            count = 0
            for symbol in symbols:
                date_today = date.today()
                if isinstance(symbol, str):
                    purchased_pps = alpaca_request_methods.get_symbol_current_price(symbol)
                else:
                    purchased_pps = symbol[1]
                qty = 1
                total_buy_price = purchased_pps
                purchase_string = ''
                date_sold = 'N/A'
                sold_pps = 'N/A'
                total_sell_price = 'N/A'
                sell_string = 'N/A'
                expected_return = purchased_pps * .03
                percentage_roi = 3.0
                actual_return = 'N/A'
                stop_loss_price = 0.00
                tp1 = purchased_pps + (purchased_pps * .03)
                tp2 = purchased_pps + (purchased_pps * .05)
                sop = purchased_pps - (purchased_pps * .01)
                if isinstance(symbol, str):
                    temporary_writer.write(f'{count},{symbol},{date_today},{purchased_pps},{qty},{total_buy_price},{purchase_string},{date_sold},{sold_pps},{total_sell_price},{sell_string},{expected_return},{percentage_roi},{actual_return},{stop_loss_price},{tp1},{tp2},{sop}\n')
                else:
                    temporary_writer.write(f'{count},{symbol[0]},{date_today},{purchased_pps},{qty},{total_buy_price},{purchase_string},{date_sold},{sold_pps},{total_sell_price},{sell_string},{expected_return},{percentage_roi},{actual_return},{stop_loss_price},{tp1},{tp2},{sop}\n')
                count += 1
            temporary_writer.close()

