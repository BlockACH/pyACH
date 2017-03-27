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
        random_data = HistoryTx().get_random_data()
        return self.wrapper(random_data)
        # data_list = history_tx.get_random_data()
        # data_list = [self.Data('AE0', '514', 'SD', 100),
        #              self.Data('AE0', '514', 'SD', 200)]

        # return history_tx.get_random_data()

    def pay_data(self):
        # TODO: change mock data with real one
        return {}
