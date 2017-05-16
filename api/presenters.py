import os
import time
import requests

import subprocess as sub
import gcoin as gcoin_lib

from flask import jsonify
from api.models import HistoryTx, TxFactory
from bank import Bank
from config import AUTHORIZED_BANKS


class BankPresenter(object):
    def __init__(self, bank_id, model):
        self.model = model
        self.bank = Bank.manager.get_bank_by_id(bank_id)

    @property
    def banks(self):
        banks = []
        if self.bank.bank_id in AUTHORIZED_BANKS:
            for bank_id in Bank.manager.bank_list:
                bank = Bank.manager.get_bank_by_id(bank_id)
                banks.append(bank.as_dict(model=self.model))
        else:
            bank = Bank.manager.get_bank_by_id(self.bank.bank_id)
            banks.append(bank.as_dict(model=self.model))
        return banks


class BaseTxPresenter(object):
    def __init__(self, bank_id, model):
        self.model = model
        self.bank = Bank.manager.get_bank_by_id(bank_id)
        self.tx_db = TxFactory.get(bank_id, self.model)

    def save_tx(self, data):
        try:
            to_hash = (
                '{receive_bank}{trigger_bank}{amount}{type}{created_time}'
                .format(**data)
            )
        except Exception:
            raise self.TxFormatError('missing tx attribute')

        key = gcoin_lib.sha256(to_hash)
        if 'key' not in data:
            data['key'] = key
        elif data['key'] != key:
            raise self.TxFormatError('key does not match')

        self.tx_db.put_tx(key, data)
        return key

    class TxFormatError(Exception):
        """wrong tx data format"""


class NotificationPresenter(BaseTxPresenter):

    def notify(self, data):
        return self.save_tx(data)


class TransactionPresenter(BaseTxPresenter):

    def query(self, trigger_bank, receive_bank, status):
        txs = self.tx_db.get_txs(trigger_bank, receive_bank, status)
        return sorted(txs, key=lambda k: k['created_time'], reverse=True)

    def remove_all(self):
        self.tx_db.remove_all()
        return jsonify(data={'message': 'Deleted!'})


class TxStateChangePresenter(BaseTxPresenter):

    def ready(self, data):
        tx_data = dict(data)
        tx_data['created_time'] = int(time.time())
        tx_data['status'] = 'ready'
        self.save_tx(tx_data)
        self.notify_other(tx_data, tx_data['receive_bank'])
        return tx_data

    def accept(self, tx_key):
        tx_data = self.update_status(tx_key, 'accepted')
        if self.model == 'smart_contract':
            tx_data, is_success = self.smart_contract_settle(tx_data)
            if not is_success:
                return tx_data
        self.notify_other(tx_data, tx_data['trigger_bank'])
        self.notify_other(tx_data, 'TCH')
        return tx_data

    def smart_contract_settle(self, tx_data):
        bank_from, bank_to = self.parse_from_and_to_bank(tx_data)
        amount = tx_data['amount']
        try:
            tx_id = bank_from.contract_send_to(bank_to, amount)
        except Exception:
            tx_data = self.reject(tx_data['key'])
            return tx_data, False
        else:
            tx_data['tx_id'] = tx_id
            self.save_tx(tx_data)
            return tx_data, True

    def reject(self, tx_key):
        tx_data = self.update_status(tx_key, 'rejected')
        self.notify_other(tx_data, tx_data['trigger_bank'])
        self.notify_other(tx_data, 'TCH')
        return tx_data

    def approve(self, tx_key):
        tx_data = self.update_status(tx_key, 'approved')
        if self.model == 'settle':
            tx_data, is_success = self.gcoin_settle(tx_data)
            if not is_success:
                return tx_data
        self.notify_other(tx_data, tx_data['trigger_bank'])
        self.notify_other(tx_data, tx_data['receive_bank'])
        return tx_data

    def gcoin_settle(self, tx_data):
        bank_from, bank_to = self.parse_from_and_to_bank(tx_data)
        amount = tx_data['amount']
        try:
            tx_id = bank_from.send_to(bank_to, amount)
        except Exception:
            tx_data = self.reject(tx_data['key'])
            return tx_data, False
        else:
            tx_data['tx_id'] = tx_id
            self.save_tx(tx_data)
            return tx_data, True

    def destroy(self, tx_key):
        tx_data = self.update_status(tx_key, 'destroyed')
        self.notify_other(tx_data, tx_data['trigger_bank'])
        self.notify_other(tx_data, tx_data['receive_bank'])
        return tx_data

    def update_status(self, tx_key, status):
        tx_data = self.tx_db.get_tx_by_key(tx_key)
        tx_data['status'] = status
        self.save_tx(tx_data)
        return tx_data

    def notify_other(self, data, bank_id_to_notify):
        bank = Bank.manager.get_bank_by_id(bank_id_to_notify)
        base_url = bank.url
        url = '{base_url}/{model}/{bank_id}/transactions/notify'.format(
            base_url=base_url,
            model=self.model,
            bank_id=bank_id_to_notify
        )
        r = requests.post(url, json=data)
        print r
        return r.json()

    def parse_from_and_to_bank(self, tx_data):
        trigger_bank = Bank.manager.get_bank_by_id(tx_data['trigger_bank'])
        receive_bank = Bank.manager.get_bank_by_id(tx_data['receive_bank'])
        if tx_data['type'] == 'SC':
            bank_from = trigger_bank
            bank_to = receive_bank
        else:
            bank_from = receive_bank
            bank_to = trigger_bank
        return bank_from, bank_to

    class TxChangeError(Exception):
        """error for tx changes"""


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
