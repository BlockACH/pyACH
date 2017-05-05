import os
import time
import requests
import json

import subprocess as sub
import gcoin as gcoin_lib

from api.models import HistoryTx, TxFactory
from bank import Bank
from config import DEMO_BANK_IP_PORT


class BaseTxPresenter(object):
    def __init__(self, bank_id, model='settle'):
        self.model = model
        self.bank_id = bank_id
        self.tx_db = TxFactory.get(self.bank_id, self.model)

    def save_tx(self, data):
        try:
            to_hash = (
                '{receive_bank}{trigger_bank}{amount}{type}{created_time}'
                .format(**data)
            )
        except Exception:
            raise self.TxFormatError('missing tx attribute')
        key = gcoin_lib.sha256(to_hash)
        self.tx_db.put_tx(key, data)
        return key

    class TxFormatError(Exception):
        """wrong tx data format"""


class NotificationPresenter(BaseTxPresenter):

    def notify(self, data):
        return self.save_tx(data)


class TransactionPresenter(BaseTxPresenter):

    def query(self, trigger_bank, receive_bank):
        txs = self.tx_db.get_tx(trigger_bank, receive_bank)
        return txs

    def remove_all(self):
        self.tx_db.remove_all()


class TriggerPresenter(BaseTxPresenter):

    def trigger(self, data):
        tx_data = dict(data)
        tx_data['created_time'] = int(time.time())
        tx_data['status'] = 'ready'
        self.save_tx(tx_data)
        self.notify_receiver(tx_data)

    def notify_receiver(self, data):
        # receive_bank_id = data['receive_bank']
        # base_url = DEMO_BANK_IP_PORT[receive_bank_id]
        # url = 'http://{base_url}/{model}/notify'.format(
        #     base_url='ach.csie.org:9877',
        #     model=self.model
        # )
        url = 'http://ach.csie.org:9877/smart_contract/notify'
        headers = {'content-type': 'application/json'}
        print url, data
        r = requests.post(url, data=json.dumps(data), headers=headers)
        print 'uuum...', r


class GcoinPresenter(object):
    def is_gcoin_alive(self):
        response = {}
        return response

    def clean_main_directory(self):
        command_list = ['gcoin-cli', 'stop']
        response = {}
        try:
            p = sub.Popen(command_list, stdout=sub.PIPE, stderr=sub.PIPE)
            output, errors = p.communicate()
        except Exception as e:
            response['status'] = 'failed'
            response['message'] = str(e)
            return response
        else:
            print 'Stop successfully!'

        main_path = os.path.join(os.path.expanduser('~'), '.gcoin/main')
        command_list = ['rm', '-rf', main_path]
        try:
            p = sub.Popen(command_list, stdout=sub.PIPE, stderr=sub.PIPE)
            output, errors = p.communicate()
        except Exception as e:
            response['status'] = 'failed'
            response['message'] = str(e)
        else:
            response['status'] = 'success'
            response['message'] = 'Clean successfully!'
        return response


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
        random_data = HistoryTx().get_random_data('SD')
        return self.wrapper(random_data)

    def pay_data(self):
        # TODO: change mock data with real one
        random_data = HistoryTx().get_random_data('SC')
        return self.wrapper(random_data)

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

    def bank_address_dict(self):
        bank_address_dict = {}
        for b in Bank.manager.bank_list:
            bank_address_dict[b] = Bank.manager.get_bank_by_id(b).address
        return bank_address_dict
