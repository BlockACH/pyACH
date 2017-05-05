import requests
import gcoin as gcoin_lib
from crypto_utils import create_ecc

from config import BANK_LIST, CLEAN_COLOR
from gcoin_presenter import GcoinPresenter
from smart_contract.utils import (create_trade_data,
                                  create_deploy_data,
                                  create_mint_data,
                                  create_clear_queue_data,
                                  create_reset_data,
                                  DEFAULT_CONTRACT_ID)


class BankManager(object):

    def __init__(self):
        self.bank_list = BANK_LIST
        self.bank_list.append('central_bank')
        self.bank_cache = {}
        self._central_bank = None
        self.tx_pool = []

    def get_bank_by_id(self, bank_id):
        if bank_id not in self.bank_list:
            bank_id = 'EA0'

        if bank_id not in self.bank_cache:
            self.bank_cache[bank_id] = Bank(bank_id)

        return self.bank_cache[bank_id]

    def get_central_bank(self):
        if not self._central_bank:
            self._central_bank = Bank('central_bank')
        return self._central_bank


bank_manager = BankManager()


class Bank(object):
    manager = bank_manager

    def __init__(self, bank_id):
        self.bank_id = bank_id
        self.priv = gcoin_lib.encode_privkey(
            gcoin_lib.sha256(bank_id),
            'wif_compressed'
        )
        self.pub = gcoin_lib.privtopub(self.priv)
        self.address = gcoin_lib.pubtoaddr(self.pub)
        self.gcoin = GcoinPresenter()
        # ECC for confidential tx
        self.ecc = create_ecc(gcoin_lib.sha256(self.bank_id))

    @property
    def balance(self):
        return self.gcoin.get_address_balance(self.address)

    @property
    def confidential_tx_priv(self):
        return self.ecc.get_privkey()

    @property
    def confidential_tx_pub(self):
        return self.ecc.get_pubkey()

    def get_contract_balance(self, contract_id):
        url = ('http://ach.csie.org:9999/smart_contract/state/{}'
               .format(contract_id))
        r = requests.get(url)
        return r.json()['balance'][self.bank_id]

    def merge_tx_in(self, color, div=50):
        self.gcoin.merge_tx_in(self.address, color, self.priv, div)

    def send_to(self, bank_to, amount, color=CLEAN_COLOR, comment=''):
        """
        This uses gcoin currency to settle. `amount` should be in BTC.
        """
        raw_tx = self.gcoin.create_raw_tx(self.address, bank_to.address,
                                          amount, color, comment)
        return self._sign_and_send_tx(raw_tx)

    def contract_send_to(self, bank_to, amount, comment='',
                         contract_id=DEFAULT_CONTRACT_ID):
        """
        This uses smart contract to settle.
        """
        contract_data = create_trade_data(self.bank_id, bank_to.bank_id,
                                          amount, comment, contract_id)
        central_bank = Bank.manager.get_central_bank()
        pub_keys = [
            central_bank.confidential_tx_pub,
            # self.confidential_tx_pub,
            # bank_to.confidential_tx_pub
        ]
        # contract_data = encrypt(contract_data, pub_keys)
        raw_tx = self.gcoin.create_raw_tx(self.address, self.address, 1,
                                          1, contract_data)
        return self._sign_and_send_tx(raw_tx)

    def contract_mint(self, amount, comment='',
                      contract_id=DEFAULT_CONTRACT_ID):
        contract_data = create_mint_data(self.bank_id, amount,
                                         comment, contract_id)
        raw_tx = self.gcoin.create_raw_tx(self.address, self.address,
                                          1, 1, contract_data)
        return self._sign_and_send_tx(raw_tx)

    def contract_clear_queue(self, comment='',
                             contract_id=DEFAULT_CONTRACT_ID):
        contract_data = create_clear_queue_data(comment, contract_id)
        raw_tx = self.gcoin.create_raw_tx(self.address, self.address,
                                          1, 1, contract_data)
        return self._sign_and_send_tx(raw_tx)

    def deploy_contract(self, contract_id=DEFAULT_CONTRACT_ID):
        deploy_data = create_deploy_data(contract_id)
        raw_tx = self.gcoin.create_raw_tx(self.address, self.address,
                                          1, 1, deploy_data)
        return self._sign_and_send_tx(raw_tx)

    def reset_contract(self, contract_id=DEFAULT_CONTRACT_ID):
        contract_data = create_reset_data(contract_id)
        raw_tx = self.gcoin.create_raw_tx(self.address, self.address,
                                          1, 1, contract_data)
        return self._sign_and_send_tx(raw_tx)

    def _sign_and_send_tx(self, raw_tx):
        signed_tx = gcoin_lib.signall(raw_tx, self.priv)
        try:
            tx_id = self.gcoin.send_raw_tx(signed_tx)
            print '#txid: {}'.format(tx_id)
            return tx_id
        except Exception as e:
            print 'SEND_RAW_TX_ERROR:', e.__dict__
            print signed_tx
            raise e
