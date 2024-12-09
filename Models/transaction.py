import sector_finder
import logging
from HistoricalFetcherAndScraper import scraper
from datetime import date, datetime
from database import transactions_DAOIMPL, transaction_model_status_DAOIMPL
import json

from MachineLearningModels import manual_alg_requisition_script

class transaction:

    def __init__(self,symbol,dp,ppps,qty,total_buy,pstring,user_id,ds = None,spps = None,tsp = None,
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
        self.result = result
        self.sector = sector_finder.get_stock_sector(self.symbol)
        self.processed = processed
        self.pol_neu_open, self.pol_pos_open, self.pol_neg_open = 0, 0, 0
        self.sa_neu_open, self.sa_pos_open, self.sa_neg_open = 0, 0, 0
        self.pol_neu_close, self.pol_pos_close, self.pol_neg_close = None, None, None
        self.sa_neu_close, self.sa_pos_close, self.sa_neg_close = None, None, None

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
        
    def create_a_base_no_loss_or_gain_transaction(user_id):
        
        symbol = 'GTI'
        qty = 1
        ppps = 0.01
        total_buy = 0.01
        user_id = user_id
        dp = date.today()
        pstring = f'{datetime.now()}-{symbol}-{dp}-{ppps}-{qty}-{total_buy}'
        ds = date.today()
        spps = 0.01
        tsp = 0.01
        sstring = f'{datetime.now()}-{symbol}-{dp}-{ppps}-{qty}-{total_buy}~sell'
        proi = 0.00
        actual = 0.00
        result = 'profit'
         

        new_transaction = transaction(symbol, dp,ppps,qty,total_buy,pstring,user_id,ds,spps,tsp,sstring,expected = (total_buy * .03),proi=proi,
                                                  actual=actual,tp1 = ppps + (ppps * .03), sop = ppps - (ppps * .01), result = result, processed = 0)
        return transactions_DAOIMPL.initial_model_creation_trans_insert(new_transaction)
        
        
# ---------------------------------------NEW FUNCTIONS NEEDING TESTS WRITTEN
    
