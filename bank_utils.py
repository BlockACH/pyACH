from config import BANK_LIST
import gcoin as gcoin_lib
from gcoin_presenter import GcoinPresenter


class BankManager(object):

    def __init__(self, BankClass):
        self.BankClass = BankClass
        self.bank_list = BANK_LIST
        self.bank_cache = {}
        self._central_bank = None

    def get_bank_by_id(self, bank_id):
        if bank_id not in self.bank_list:
            bank_id = 'EA0'

        if bank_id not in self.bank_cache:
            self.bank_cache[bank_id] = self.BankClass(bank_id)

        return self.bank_cache[bank_id]

    def get_central_bank(self):
        if not self._central_bank:
            self._central_bank = self.BankClass('central_bank')
        return self._central_bank


class SigletonBankManagerFactory(object):
    provided_managers = {}

    def get_bank_manager(self, BankClass):
        if BankClass not in self.provided_managers:
            self.provided_managers[BankClass] = BankManager(BankClass)
        return self.provided_managers[BankClass]


sigleton_bank_manager_factory = SigletonBankManagerFactory()


class BaseBank(object):
    class __metaclass__(type):
        @property
        def manager(cls):
            """
            call `Bank.manager` to get a sigleton bank manager
            """
            return sigleton_bank_manager_factory.get_bank_manager(cls)

    def __init__(self, bank_id):
        self.bank_id = bank_id
        self.priv = gcoin_lib.encode_privkey(gcoin_lib.sha256(bank_id),
                                             'wif_compressed')
        self.pub = gcoin_lib.privtopub(self.priv)
        self.address = gcoin_lib.pubtoaddr(self.pub)
        self.gcoin = GcoinPresenter()
