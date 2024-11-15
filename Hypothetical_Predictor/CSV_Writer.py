
from datetime import date
import alpaca_request_methods

class CSV_Writer:

    def write_temporary_csv(symbols):
        with open('/home/ubuntu/TradeWiseTrainingModelComparison/Hypothetical_Predictor/transactions.csv', 'w') as temporary_writer:
            temporary_writer.write(f'id,symbol,dp,ppps,qty,total_buy,pstring,ds,spps,tsp,sstring,expected,proi,actual,tp1,sop,result,user_id,processed\n')
            count = 0
            
            for symbol in symbols:
                date_today = date.today()
                if isinstance(symbol, str):
                    ppps = alpaca_request_methods.get_symbol_current_price(symbol)
                else:
                    ppps = symbol[1]
                qty = 1
                total_buy = ppps
                pstring = ''
                ds = 'N/A'
                spps = 'N/A'
                tsp = 'N/A'
                sstring = 'N/A'
                expected = ppps * .03
                proi = 0.00
                actual = 'N/A'
                tp1 = ppps + (ppps * .03)
                sop = ppps - (ppps * .01)
                if isinstance(symbol, str):
                    temporary_writer.write(f'{count},{symbol},{date_today},{ppps},{qty},{total_buy},{pstring},{ds},{spps},{tsp},{sstring},{expected},{proi},{actual},{tp1},{sop}\n')
                else:
                    temporary_writer.write(f'{count},{symbol[0]},{date_today},{ppps},{qty},{total_buy},{pstring},{ds},{spps},{tsp},{sstring},{expected},{proi},{actual},{tp1},{sop}\n')
                count += 1
            temporary_writer.close()

