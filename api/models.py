from pymongo import MongoClient
import random

BANK_LIST = [
    '6AB', 'A28', '46E', 'DD3', '822', 'CCC', '219',
    '18C', '170', 'B63', '62F', '5E0', '666', '519',
    'BA4', '5BD', '682', 'E07', 'B31', '0B1', 'FCB',
    'B89', '101', 'EDB', 'E75', '75D', 'A0D', '22D',
    'AB5', 'A1D', 'F73', 'C45', '481', '49A', 'EE0',
    '269', '7BA', '48C', 'E0C', 'CE3', '8DA', '552',
    '1F6', 'B30', '6D4', 'FB4', '4AD', '940', '838',
    'E15', 'F8E', '717', 'C72', '882', 'EA0'
]

TX_TYPE_LIST = ['SC', 'SD']

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
    db_url = 'mongodb://ach:graduate@13.78.116.125:27017/ach'
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

    def get_collect_data(self):
        cursor = self.collection.find()
        pass

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
