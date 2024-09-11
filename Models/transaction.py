import sector_finder

class transaction:

    def __init__(self,symbol,date_purchased,purchased_pps,qty,total_buy_price,purchase_string,
                 date_sold = 'N/A',sold_pps = 'N/A',total_sell_price = 'N/A',sell_string = 'N/A',expected_return = 0.00,percentage_roi =0.0,
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

    def aggregate_sectors_for_stock_symbols(symbols):
        sectors = {}
        for symbol in symbols:
            sector = sector_finder.get_stock_sector(symbol[0])
            print(sector, symbol)
            # Aggregate the sectors by counting occurrences
            if sector in sectors:
                sectors[sector] += 1  # Increment the count if the sector already exists
            else:
                sectors[sector] = 1  # Initialize the sector count if it doesn't exist yet
        
        return sectors  # Return the aggregated sector counts