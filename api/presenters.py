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
        cursor = HistoryTx().get_range_data_cursor(start_date, end_date)
        return self.wrapper(cursor[0])

    def db_settle(self, start_date, end_date):
        cursor = HistoryTx().get_range_data_cursor(start_date, end_date)
        bank_dict = {}
        for tx in cursor:
            p_bank = str(tx['P_PBANK'][:3])
            r_bank = str(tx['P_RBANK'][:3])
            amount = float(tx['P_AMT'])
            if tx['P_TDATE'] == start_date:
                if tx['P_TYPE'] == 'N' and tx['P_TXTYPE'] == 'SD':
                    bank_dict[r_bank] = bank_dict.get(r_bank, 0) - amount
                    bank_dict[p_bank] = bank_dict.get(p_bank, 0) + amount
            elif tx['P_TDATE'] == end_date:
                if tx['P_TXTYPE'] == 'SC':
                    bank_dict[r_bank] = bank_dict.get(r_bank, 0) + amount
                    bank_dict[p_bank] = bank_dict.get(p_bank, 0) - amount
                elif tx['P_TYPE'] == 'R' and tx['P_TXTYPE'] == 'SD':
                    bank_dict[r_bank] = bank_dict.get(r_bank, 0) - amount
                    bank_dict[p_bank] = bank_dict.get(p_bank, 0) + amount

        return bank_dict
