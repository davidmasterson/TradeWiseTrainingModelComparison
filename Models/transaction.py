
class transaction:

    def __init__(self,symbol,date_purchased,purchased_pps,qty,total_buy_price,purchase_string,
                 date_sold = 'N/A',sold_pps = 'N/A',total_sell_price = 'N/A',sell_string = 'N/A',expected_return = 0.00,percentage_roi ='N/A',
                 actual_return = 'N/A',stop_loss_price = 0.00,tp1 = 0.00,tp2 = 0.00,sop = 0.00):
        self.symbol = symbol
        self.date_purchased = date_purchased
        self.purchased_pps = purchased_pps
        self.qty = qty
        self.total_buy_price = total_buy_price
        self.purchase_string = purchase_string
        self.date_sold = date_sold
        self.sold_pps = sold_pps
        self.total_sell_price = total_sell_price
        self.sell_string = sell_string
        self.expected_return = expected_return
        self.percentage_roi = percentage_roi
        self.actual_return = actual_return
        self.stop_loss_price = stop_loss_price
        self.tp1 = tp1
        self.tp2 = tp2
        self.sop = sop