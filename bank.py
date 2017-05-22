import requests
import gcoin as gcoin_lib
from crypto_utils import create_ecc, encrypt

from config import (
    BANK_LIST, BANK_URL, CLEAN_COLOR, CONTRACT_SERVER_URL
)
from gcoin_presenter import GcoinPresenter
from smart_contract.utils import (
    create_trade_data, create_deploy_data,
    create_mint_data, create_batch_settle_data,
    create_reset_data, DEFAULT_CONTRACT_ID
)


class BankManager(object):

    def __init__(self):
        self.bank_list = BANK_LIST
        self.bank_cache = {}
        self._tch = None
        self._central_bank = None
        self.tx_pool = []

    def get_bank_by_id(self, bank_id):
        if (
            bank_id not in self.bank_list and
            bank_id != 'TCH' and
            bank_id != 'central_bank'
        ):
            bank_id = 'EA0'

        if bank_id not in self.bank_cache:
            self.bank_cache[bank_id] = Bank(bank_id)

        return self.bank_cache[bank_id]

    def get_central_bank(self):
        if not self._central_bank:
            self._central_bank = Bank('central_bank')
        return self._central_bank

    def get_tch(self):
        if not self._tch:
            self._tch = Bank('TCH')
        return self._tch


bank_manager = BankManager()


class Bank(object):
    manager = bank_manager

    def __init__(self, bank_id):
        self.bank_id = str(bank_id)
        self.priv = gcoin_lib.encode_privkey(
            gcoin_lib.sha256(self.bank_id),
            'wif_compressed'
        )
        self.pub = gcoin_lib.privtopub(self.priv)
        self.address = gcoin_lib.pubtoaddr(self.pub)
        self.gcoin = GcoinPresenter()
        self.url = BANK_URL.get(self.bank_id)
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

    def as_dict(self, model='settle', contract_id=DEFAULT_CONTRACT_ID):
        result_dict = {
            'bank_id': self.bank_id,
            'address': self.address,
        }

        if model == 'settle':
            result_dict['balance'] = float(self.balance[CLEAN_COLOR])
        else:
            result_dict['balance'] = self.get_contract_balance(contract_id)
            result_dict['unsettled_balance'] = (
                self.get_contract_unsettled_balance(contract_id)
            )

        return result_dict

    def get_contract_balance(self, contract_id=DEFAULT_CONTRACT_ID):
        url = '{server_url}/smart_contract/state/{contract_id}'.format(
            server_url=CONTRACT_SERVER_URL,
            contract_id=contract_id
        )
        r = requests.get(url)
        balances = r.json().get('balance', {})
        return balances.get(self.bank_id, 'N/A')

    def get_contract_unsettled_balance(self, contract_id=DEFAULT_CONTRACT_ID):
        url = '{server_url}/smart_contract/state/{contract_id}'.format(
            server_url=CONTRACT_SERVER_URL,
            contract_id=contract_id
        )
        r = requests.get(url)
        balances = r.json().get('unsettled_balance', {})
        return balances.get(self.bank_id, 'N/A')

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
        tch = Bank.manager.get_tch()
        pub_keys = [
            tch.confidential_tx_pub,
            self.confidential_tx_pub,
            bank_to.confidential_tx_pub
        ]
        contract_data = encrypt(contract_data, pub_keys)
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

    def contract_batch_settle(self, comment='',
                              contract_id=DEFAULT_CONTRACT_ID):
        contract_data = create_batch_settle_data(comment, contract_id)
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
