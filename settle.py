from pymongo import MongoClient
from gcoin_presenter import GcoinPresenter
from bank import BankManager, Bank

uri = "mongodb://ach.csie.org:27017/ach"
astar_mongo = MongoClient(uri)
db = astar_mongo['ach']
collection = db['transactions']
filter = {
    "$or": [
        {
            "P_TDATE": "01050622"
        },
        {
            "P_TDATE": "01050621",
            "P_TYPE": "N"
        }
    ]
}

txs = collection.find(filter)
print 'r size:', txs.count()

for tx in txs:
    print 'P_PBANK', tx['P_PBANK']
    pBank = Bank.manager.get_bank_by_id(str(tx['P_PBANK'][:3]))
    rBank = Bank.manager.get_bank_by_id(str(tx['P_RBANK'][:3]))
    signed_tx = pBank.send_to(rBank, float(tx['P_AMT']), 2, 'pymongo yo')

    # print 'pBank', pBank
    print 'signed_tx', signed_tx
    # print 'tx:', tx[]
