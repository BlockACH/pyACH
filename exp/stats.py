import time
import json

from pymongo import MongoClient

BANK_LIST = [
    '6AB', 'A28', '46E', 'DD3', '822', 'CCC', '219',
    '18C', '170', 'B63', '62F', '5E0', '666', '519',
    'BA4', '5BD', '682', 'E07', 'B31', '0B1', 'FCB',
    'B89', '101', 'EDB', 'E75', '75D', 'A0D', '22D',
    'AB5', 'A1D', 'F73', 'C45', '481', '49A', 'EE0',
    '269', '7BA', '48C', 'E0C', 'CE3', '8DA', '552',
    '1F6', 'B30', '6D4', 'FB4', '4AD', '940', '838',
    'E15', 'F8E', '717', 'C72', '882', 'EA0'
]

VALID_DATE_LIST = [
    '01050601', '01050602', '01050603', '01050604',
    '01050606', '01050607', '01050608', '01050613',
    '01050614', '01050615', '01050616', '01050617',
    '01050620', '01050621', '01050622', '01050623',
    '01050624', '01050627', '01050628', '01050629',
    '01050630', '01050701', '01050704', '01050705',
    '01050706', '01050707', '01050708', '01050711',
    '01050712', '01050713', '01050714', '01050715',
    '01050718', '01050719', '01050720', '01050721',
    '01050722', '01050725', '01050726', '01050727',
    '01050728', '01050729', '01050801', '01050802',
    '01050803', '01050804', '01050805', '01050808',
    '01050809', '01050810', '01050811', '01050812',
    '01050815', '01050816', '01050817', '01050818',
    '01050819', '01050822', '01050823', '01050824',
    '01050825', '01050826', '01050829', '01050830',
    '01050831'
]

uri = 'mongodb://ach:graduate@localhost:27017/ach'
astar_mongo = MongoClient(uri)
db = astar_mongo['ach']
collection = db['transactions']



def get_filter(previous_day, current_day):
    return {
        "$or":[{ "P_TDATE": current_day },
            { "P_TDATE": previous_day, "P_TYPE": "N" }]
    }

def add_bank_count(bank, table, bank_list):
    if bank not in bank_list:
        table['EA0'] += 1
    else:
        table[bank] += 1

for i, date_string in enumerate(VALID_DATE_LIST):
    previous_day = date_string
    current_day = VALID_DATE_LIST[i + 1]

    filter = get_filter(previous_day, current_day)
    table = dict((el,0) for el in BANK_LIST)
    rest_count = 0
    count = 0
    txs = collection.find(filter, no_cursor_timeout=True)

    for tx in txs:
        count += 1
        p_bank = str(tx['P_PBANK'][:3])
        r_bank = str(tx['P_RBANK'][:3])
        if tx['P_TDATE'] == previous_day:
            if tx['P_TYPE'] == 'N' and tx['P_TXTYPE'] == 'SD':
                add_bank_count(r_bank, table, BANK_LIST)
            else:
                rest_count += 1
        elif tx['P_TDATE'] == current_day:
            if tx['P_TXTYPE'] == 'SC':
                add_bank_count(p_bank, table, BANK_LIST)
            elif tx['P_TYPE'] == 'R' and tx['P_TXTYPE'] == 'SD':
                add_bank_count(r_bank, table, BANK_LIST)
            else:
                rest_count += 1

    # print json.dumps(table, indent=4)
    print '##### {} to {} #####'.format(previous_day, current_day)
    print 'txs count is {}'.format(count)
    print 'sum of table.values() is {}'.format(sum(table.values()))
    print 'max of table.values() is {}'.format(max(table.values()))
    # print 'rest_count is {}'.format(rest_count)
