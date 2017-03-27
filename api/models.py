from pymongo import MongoClient


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
            return self.__dict__[attr_name]
        else:
            raise AttributeError('`{}` attribute should be defined'.format(attr_name))


class HistoryTx(BaseDbModel):
    db_url = 'mongodb://13.78.116.125:27017/ach'
    db_name = 'ach'
    collection_name = 'transactions'


class Tx(BaseDbModel):
    """
    trigger_bank, receive_bank, type, amount, tx_id, status
    """
    pass
