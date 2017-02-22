import json
import time

from pymongo import MongoClient
from gcoin_presenter import GcoinPresenter
from bank import BankManager, Bank
from config import ASTAR_MONGO_URI
from bson.json_util import dumps

BTC_NUM = 10**8

astar_mongo = MongoClient(ASTAR_MONGO_URI)
db = astar_mongo['ach']
collection = db['pythonTransactions']

previous_day = '01050601'
current_day = '01050602'

filter = {
    "$or": [
        {
            "P_TDATE": previous_day
        },
        {
            "P_TDATE": current_day,
            "P_TYPE": "N"
        }
    ]
}

# db.txs.find({
#     "$or": [
#         {
#             "P_TDATE": "01050601"
#         },
#         {
#             "P_TDATE": "01050602",
#             "P_TYPE": "N"
#         }
#     ]
# }).size()

txs = collection.find(filter, no_cursor_timeout=True)
print ('r size: {}'.format(txs.count()))
count = 0
bank_dict = {}
start = time.time()
for tx in txs:
    count += 1
    # p_bank, r_bank, amount = tx
    p_bank = Bank.manager.get_bank_by_id(str(tx['P_PBANK'][:3]))
    r_bank = Bank.manager.get_bank_by_id(str(tx['P_RBANK'][:3]))
    p_tdate = str(tx['P_TDATE'])
    amount = float(tx['P_AMT']) / BTC_NUM
    # signed_tx = pBank.send_to(rBank, float(tx['P_AMT'])/BTC_NUM, 2, 'pymongo yo')
    print ('------------- COUNT: {} -------------'.format(count))
    if count % 5000 == 0:
        print ('Took {} seconds.'.format(time.time() - start))
        print ('MERGING INPUTS...')
        for bank_id in Bank.manager.bank_list:
            bank = Bank.manager.get_bank_by_id(bank_id)
            bank.merge_tx_in(color=2, div=20)
        print ('[DONE] MERGING INPUTS...')

    print ('PBANK: {}, RBANK: {}, AMOUNT: {}, P_TDATE: {}'.format(p_bank.bank_id, r_bank.bank_id, amount, p_tdate))
    print ('transaction: {}'.format(dumps(tx, indent=4)))
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

print (bank_dict)

astar_mongo.close()
