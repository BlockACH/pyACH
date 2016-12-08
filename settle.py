import time

from pymongo import MongoClient
from gcoin_presenter import GcoinPresenter
from bank import BankManager, Bank

BTC_NUM = 10**8

uri = "mongodb://ach.csie.org:27017/ach"
astar_mongo = MongoClient(uri)
db = astar_mongo['ach']
collection = db['transactions']

previous_day = '01050621'
current_day = '01050622'

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
count = 0
start = time.time()
for tx in txs:
    count += 1
    p_bank = Bank.manager.get_bank_by_id(str(tx['P_PBANK'][:3]))
    r_bank = Bank.manager.get_bank_by_id(str(tx['P_RBANK'][:3]))
    amount = float(tx['P_AMT']) / BTC_NUM
    #signed_tx = pBank.send_to(rBank, float(tx['P_AMT'])/BTC_NUM, 2, 'pymongo yo')
    print '------------- COUNT: {} -------------'.format(count)
    if count % 1000 == 0:
        print 'Took {} seconds.'.format(time.time() - start)
        
    print 'PBANK: {}, RBANK: {}, AMOUNT: {}'.format(p_bank.bank_id, r_bank.bank_id, amount)
    if tx['P_TDATE'] == previous_day:
        if tx['P_TYPE'] == 'N' and tx['P_TXTYPE'] == 'SD':
            r_bank.send_to(p_bank, amount, 2, 'prev N SD')
    elif tx['P_TDATE'] == current_day:
        if tx['P_TXTYPE'] == 'SC':
            p_bank.send_to(r_bank, amount, 2, 'current SC')
        elif tx['P_TYPE'] == 'R' and tx['P_TXTYPE'] == 'SD':
            r_bank.send_to(p_bank, amount, 2, 'current R SD')
