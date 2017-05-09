import json
import random
import plyvel

from pymongo import MongoClient
from config import (
    BANK_LIST, SMART_CONTRACT_DB_PATH, SETTLE_DB_PATH
)


class HistoryTx(object):
    db_url = 'mongodb://ach:graduate@ach.csie.org:27017/ach'
    db_name = 'ach'
    collection_name = 'transactions'

    def __init__(self):
        mongo = MongoClient(self.db_url)
        self.db = mongo[self.db_name]
        self.collection = self.db[self.collection_name]

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


class TxFactory(object):
    @staticmethod
    def get(bank_id, model):
        if model == 'settle':
            db_path = '{base}/{bank}'.format(
                base=SETTLE_DB_PATH,
                bank=bank_id,
            )
            return Tx(db_path)
        elif model == 'smart_contract':
            db_path = '{base}/{bank}'.format(
                base=SMART_CONTRACT_DB_PATH,
                bank=bank_id,
            )
            return Tx(db_path)
        return None


class Tx(object):
    """
    trigger_bank, receive_bank, type, amount, status, created_time,
    tx_id(gcoin)
    """
    def __init__(self, db_path):
        self.db = plyvel.DB(db_path, create_if_missing=True)

    def get_db_path(self):
        if hasattr(self, 'db_path'):
            return getattr(self, 'db_path')
        else:
            raise AttributeError(
                '`{}` attribute should be defined'.format('db_path')
            )

    def get_tx(self, trigger_bank, receive_bank):
        return_list = []
        for key, value in self.db.iterator():
            json_value = json.loads(value)
            if trigger_bank:
                if json_value['trigger_bank'] == trigger_bank:
                    return_list.append(json_value)
            elif receive_bank:
                if json_value['receive_bank'] == receive_bank:
                    return_list.append(json_value)
            else:
                return_list.append(json_value)
        return return_list

    def put_tx(self, key, tx):
        self.db.put(key, json.dumps(tx))

    def get_tx_by_key(self, key):
        tx_data = self.db.get(str(key))
        return json.loads(tx_data)

    def remove_all(self):
        for key, value in self.db.iterator():
            self.db.delete(key)
