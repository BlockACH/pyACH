import time
import csv
import json

from pymongo import MongoClient
from gcoin_presenter import GcoinPresenter
from bank import BankManager, Bank
from config import ASTAR_MONGO_URI

astar_mongo = MongoClient(ASTAR_MONGO_URI)
db = astar_mongo['ach']

BTC_NUM = 10**8

achCsvHeader = [
  'P_TDATE',
  'P_SCHD',
  'P_TYPE',
  'P_SEQ',
  'P_PBANK',
  'P_CID',
  'P_TTIME',
  'P_TXTYPE',
  'P_TXID',
  'P_PCLNO',
  'P_RBANK',
  'P_RCLNO',
  'P_AMT',
  'P_RCODE',
  'P_PID',
  'P_SID',
  'P_PDATE',
  'P_PSEQ',
  'P_PSCHD',
  'P_CNO',
  'P_NOTE',
  'P_FILLER',
  'P_STAT',
  'IS_DELEGATE',
  'IMP_OPBK_ID',
];

count = 0
with open('../data/ach/txdata_bc_10506_TDES_20161005111019.csv', 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',')
    bulk = db.pythonTransactions.initialize_ordered_bulk_op()
    for row in spamreader:
        tx = dict(zip(achCsvHeader, row))
        bulk.insert(tx)
        count += 1
        if count % 20000 == 0:
            result = bulk.execute()
            bulk = db.pythonTransactions.initialize_ordered_bulk_op()
            print count
            print json.dumps(result, indent=4)
            count = 0
    if count > 0:
        result = bulk.execute()
        print count
        print json.dumps(result, indent=4)

