from collections import namedtuple

from models import HistoryTx


class HistoryDataPresenter(object):

    def wrapper(self, data):
        return {
            'trigger_bank': data['P_PBANK'][:3],
            'receive_bank': data['P_RBANK'][:3],
            'tx_type': data['P_TXTYPE'],
            'amount': float(data['P_AMT'])
        }

    def collect_data(self):
        # TODO: change mock data with real one
        random_data = HistoryTx().get_random_data('SC')
        return self.wrapper(random_data)

    def pay_data(self):
        # TODO: change mock data with real one
        return {}

    def range_data(self, start_date, end_date):
        return self.wrapper(HistoryTx().get_range_data(start_date, end_date))
