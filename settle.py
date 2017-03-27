import time

from pymongo import MongoClient
from bank import Bank

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

txs = collection.find(filter, no_cursor_timeout=True)
print 'r size:', txs.count()
count = 0
bank_dict = {}
start = time.time()
for tx in txs:
    count += 1
    # p_bank, r_bank, amount = tx
    p_bank = Bank.manager.get_bank_by_id(str(tx['P_PBANK'][:3]))
    r_bank = Bank.manager.get_bank_by_id(str(tx['P_RBANK'][:3]))
    amount = float(tx['P_AMT']) / BTC_NUM
    # signed_tx = pBank.send_to(rBank, float(tx['P_AMT'])/BTC_NUM, 2, 'pymongo yo')
    print '------------- COUNT: {} -------------'.format(count)
    if count % 5000 == 0:
        print 'Took {} seconds.'.format(time.time() - start)
        print 'MERGING INPUTS...'
        for bank_id in Bank.manager.bank_list:
            bank = Bank.manager.get_bank_by_id(bank_id)
            bank.merge_tx_in(color=2, div=20)
        print '[DONE] MERGING INPUTS...'

    print 'PBANK: {}, RBANK: {}, AMOUNT: {}'.format(p_bank.bank_id, r_bank.bank_id, amount)
    if tx['P_TDATE'] == previous_day:
        if tx['P_TYPE'] == 'N' and tx['P_TXTYPE'] == 'SD':
            r_bank.send_to(p_bank, amount, 2, 'prev N SD')
            bank_dict[r_bank.bank_id] = bank_dict.get(r_bank.bank_id, 0) - amount * BTC_NUM
            bank_dict[p_bank.bank_id] = bank_dict.get(p_bank.bank_id, 0) + amount * BTC_NUM
    elif tx['P_TDATE'] == current_day:
        if tx['P_TXTYPE'] == 'SC':
            p_bank.send_to(r_bank, amount, 2, 'current SC')
            bank_dict[r_bank.bank_id] = bank_dict.get(r_bank.bank_id, 0) + amount * BTC_NUM
            bank_dict[p_bank.bank_id] = bank_dict.get(p_bank.bank_id, 0) - amount * BTC_NUM
        elif tx['P_TYPE'] == 'R' and tx['P_TXTYPE'] == 'SD':
            r_bank.send_to(p_bank, amount, 2, 'current R SD')
            bank_dict[r_bank.bank_id] = bank_dict.get(r_bank.bank_id, 0) - amount * BTC_NUM
            bank_dict[p_bank.bank_id] = bank_dict.get(p_bank.bank_id, 0) + amount * BTC_NUM

print bank_dict

astar_mongo.close()
