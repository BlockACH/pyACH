import gcoin as gcoin_lib
from gcoin_presenter import GcoinPresenter
from config import BANK_LIST

class BankManager(object):

    def __init__(self):
        self.bank_list = BANK_LIST
        self.bank_cache = {}
        self._central_bank = None

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
        self.priv = gcoin_lib.encode_privkey(gcoin_lib.sha256(bank_id), 'wif_compressed')
        self.pub = gcoin_lib.privtopub(self.priv)
        self.address = gcoin_lib.pubtoaddr(self.pub)
        self.gcoin = GcoinPresenter()

    def send_to(self, bank_to, amount, color, comment=''):
        raw_tx = self.gcoin.create_raw_tx(self.address, bank_to.address, amount, color, comment)
        print 'raw tx done...'
        signed_tx = gcoin_lib.signall(raw_tx, self.priv)
        print 'sign tx done...'
        try:
            tx_id = self.gcoin.send_raw_tx(signed_tx)
            return tx_id
        except Exception as e:
            print 'QQ:', e.__dict__
            print signed_tx
            raise e

    def merge_tx_in(self, color, div=50):
        self.gcoin.merge_tx_in(self.address, color, self.priv, div)

    @property
    def balance(self):
        return self.gcoin.get_address_balance(self.address)

def test():
    b1 = Bank.manager.get_bank_by_id('6AB')
    b2 = Bank.manager.get_bank_by_id('EA0')
    for bank_id in BANK_LIST:
        b = Bank.manager.get_bank_by_id(bank_id)
        print b.address, b.balance
    #print b1.send_to(b2, 10, 1, 'wow')
