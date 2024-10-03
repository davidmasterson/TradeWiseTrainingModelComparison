import sector_finder
import logging

class transaction:

    def __init__(self,symbol,dp,ppps,qty,total_buy,pstring,user_id,ds = 'N/A',spps = 'N/A',tsp = 'N/A',
                 sstring = 'N/A',expected = 0.00,proi =0.0,actual = 'N/A',tp1 = 0.00, sop = 0.00, prediction=1, result = None):
        self.symbol = symbol
        self.dp = dp
        self.ppps = ppps
        self.qty = qty
        self.total_buy = total_buy
        self.pstring = pstring
        self.user_id = user_id
        self.ds = ds
        self.spps = spps
        self.tsp = tsp
        self.sstring = sstring
        self.expected = expected
        self.proi = proi
        self.actual = actual
        self.tp1 = tp1
        self.sop = sop
        self.prediction = prediction
        self.result = result

    def aggregate_sectors_for_stock_symbols(symbols):
        sectors = {}
        for symbol in symbols:
            sector = sector_finder.get_stock_sector(symbol[0])
            logging.info(sector, symbol)
            # Aggregate the sectors by counting occurrences
            if sector in sectors:
                sectors[sector] += 1  # Increment the count if the sector already exists
            else:
                sectors[sector] = 1  # Initialize the sector count if it doesn't exist yet
        
        return sectors  # Return the aggregated sector counts