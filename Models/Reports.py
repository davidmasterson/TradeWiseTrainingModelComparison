from datetime import date, datetime
from EmailSender import email_sender
from database import transactions_DAOIMPL, user_DAOIMPL
import logging

class Report:
    
    def __init__(self, user_object, user_id, report_data = None):
        self.user_id = user_id
        self.user = user_object
        self.report_data = report_data
        
        
    def create_and_send_end_of_day_report(self):
        try:
            logging.info(f'{datetime.now()}: Started end of day clean up for user {self.user["user_name"]}')
            # End-of-day cleanup
            closed_trans = transactions_DAOIMPL.get_transactions_for_user_by_sell_date(self.user_id, date.today())
            opened_trans = transactions_DAOIMPL.get_transactions_for_user_by_purchase_date(self.user_id, date.today())

            # Prepare opened and closed positions as lists of dictionaries for better formatting in HTML
            opens = []
            for trp in opened_trans:
                symbol = trp[1]
                purchase_price = float(trp[3])
                qty = int(trp[4])
                total_purchase = purchase_price * qty
                opens.append({
                    "symbol": symbol,
                    "qty": qty,
                    "purchase_price": purchase_price,
                    "total_purchase": total_purchase
                })

            closes = []
            for trs in closed_trans:
                symbol = trs[1]
                purchase_price = float(trs[3])
                qty = int(trs[4])
                total_purchase = purchase_price * qty
                sell_price = float(trs[8])
                total_sell = float(trs[9])
                actual_return = float(trs[13])
                percentroi = float(trs[12])
                closes.append({
                    "symbol": symbol,
                    "qty": qty,
                    "purchase_price": purchase_price,
                    "total_purchase": total_purchase,
                    "sell_price": sell_price,
                    "total_sell": total_sell,
                    "actual_return": actual_return,
                    "percentroi": percentroi
                })

            # Send email using structured data
            email_sender.send_email_of_closed_positions(opens, closes, self.user_id)
        except Exception as e:
            logging.error(f'Unable to send end of day report to {self.user["user_name"]} due to {e}')   