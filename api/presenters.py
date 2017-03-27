from collections import namedtuple

from models import HistoryTx


class HistoryDataPresenter(object):
    Data = namedtuple(
        'Data',
        ['trigger_bank', 'receive_bank', 'type', 'amount']
    )

    def to_dict_data(self, data_list):
        return [d._asdict() for d in data_list]

    def collect_data(self):
        # TODO: change mock data with real one
        data_list = [self.Data('AE0', '514', 'SD', 100),
                     self.Data('AE0', '514', 'SD', 200)]

        return self.to_dict_data(data_list)

    def pay_data(self):
        # TODO: change mock data with real one
        data_list = [self.Data('AE0', '514', 'SC', 100),
                     self.Data('AE0', '514', 'SC', 200)]

        return self.to_dict_data(data_list)
