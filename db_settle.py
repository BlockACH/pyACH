import time

from pymongo import MongoClient

uri = 'mongodb://ach:graduate@13.78.116.125:27017/ach'
astar_mongo = MongoClient(uri)
db = astar_mongo['ach']
collection = db['transactions']

previous_day = '01050531'
current_day = '01050601'

query = {
    "$or": [
        {
            "P_TDATE": current_day
        },
        {
            "P_TDATE": previous_day,
            "P_TYPE": "N"
        }
    ]
}

txs = collection.find(query, no_cursor_timeout=True)
print 'r size:', txs.count()
count = 0
bank_dict = {}
start = time.time()

for tx in txs:
    count += 1
    p_bank = str(tx['P_PBANK'][:3])
    r_bank = str(tx['P_RBANK'][:3])
    amount = float(tx['P_AMT'])

    print '------------- COUNT: {} -------------'.format(count)
    if count % 5000 == 0:
        print 'Took {} seconds.'.format(time.time() - start)

    print 'PBANK: {}, RBANK: {}, AMOUNT: {}'.format(p_bank, r_bank, amount)
    if tx['P_TDATE'] == previous_day:
        if tx['P_TYPE'] == 'N' and tx['P_TXTYPE'] == 'SD':
            bank_dict[r_bank] = bank_dict.get(r_bank, 0) - amount
            bank_dict[p_bank] = bank_dict.get(p_bank, 0) + amount
    elif tx['P_TDATE'] == current_day:
        if tx['P_TXTYPE'] == 'SC':
            bank_dict[r_bank] = bank_dict.get(r_bank, 0) + amount
            bank_dict[p_bank] = bank_dict.get(p_bank, 0) - amount
        elif tx['P_TYPE'] == 'R' and tx['P_TXTYPE'] == 'SD':
            bank_dict[r_bank] = bank_dict.get(r_bank, 0) - amount
            bank_dict[p_bank] = bank_dict.get(p_bank, 0) + amount

print bank_dict
astar_mongo.close()
