import sector_finder
import logging
import yahoo_finance
from MachineLearningModels import manual_alg_requisition_script

class transaction:

    def __init__(self,symbol,dp,ppps,qty,total_buy,pstring,user_id,sentiment,ds = None,spps = None,tsp = None,
                 sstring = None,expected = 0.00,proi =0.0,actual = None,tp1 = 0.00, sop = 0.00, result = None, processed = 0):
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
        self.sentiment = sentiment
        self.result = result
        self.sector = sector_finder.get_stock_sector(self.symbol)
        self.processed = processed
        self.pol_neu_open, self.pol_pos_open, self.pol_neg_open = manual_alg_requisition_script.process_daily_political_sentiment()
        self.sa_neu_open, self.sa_pos_open, self.sa_neg_open = transaction.calculate_sentiment(self.symbol)

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
    
    def calculate_sentiment(symbol):
        try:
            info = manual_alg_requisition_script.request_articles(symbol)
            avg_neut, avg_pos, avg_neg = manual_alg_requisition_script.process_phrase_for_sentiment(info)
            logging.info(f'Sentiment is {avg_neut, avg_pos, avg_neg}')
            return avg_neut, avg_pos, avg_neg 
        except Exception as e:
            logging.error(f'Error calculating sentiment: {e}')
            return 0, 0, 0