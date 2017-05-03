import random

from pymongo import MongoClient
from config import BANK_LIST

class BaseDbModel(object):

    def __init__(self):
        mongo = MongoClient(self.get_db_url())
        self.db = mongo[self.get_db_name()]
        self.collection = self.db[self.get_collection_name()]

    def get_db_url(self):
        return self._get_attribute('db_url')

    def get_db_name(self):
        return self._get_attribute('db_name')

    def get_collection_name(self):
        return self._get_attribute('collection_name')

    def _get_attribute(self, attr_name):
        if hasattr(self, attr_name):
            return getattr(self, attr_name)
        else:
            raise AttributeError('`{}` attribute should be defined'.format(attr_name))


class HistoryTx(BaseDbModel):
    db_url = 'mongodb://ach:graduate@ach.csie.org:27017/ach'
    db_name = 'ach'
    collection_name = 'transactions'

    def get_query_dict(self, start_date, end_date):
        return {
            '$or': [
                {
                    'P_TDATE': end_date
                },
                {
                    'P_TDATE': start_date,
                    'P_TYPE': 'N'
                }
            ]
        }

    def get_random_data(self, tx_type):
        return {
            'P_PBANK': BANK_LIST[random.randint(0, len(BANK_LIST))],
            'P_RBANK': BANK_LIST[random.randint(0, len(BANK_LIST))],
            'P_TXTYPE': tx_type,
            'P_AMT': random.randint(0, 10) * 1000
        }

    def get_range_data_cursor(self, start_date, end_date):
        query = self.get_query_dict(start_date, end_date)
        cursor = self.collection.find(query, no_cursor_timeout=True)
        return cursor

class Tx(BaseDbModel):
    db_url = 'mongodb://ach:graduate@13.78.116.125:27017/tx'
    db_name = 'tx'
    collection_name = 'transactions'
    """
    trigger_bank, receive_bank, type, amount, tx_id, status
    """
    pass
