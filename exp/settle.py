import time
import logging

from pymongo import MongoClient
from bank import Bank

from exp.init_bank import reset_all_bank_balance
BTC_NUM = 10**8


def count_transaction_num(previous_day, current_day):
    uri = 'mongodb://ach:graduate@localhost:27017/ach'
    astar_mongo = MongoClient(uri)
    db = astar_mongo['ach']
    collection = db['transactions']
    query = {
        "$or": [
            {
                "P_TDATE": current_day,
                "P_TYPE": "R",
                "P_TXTYPE": "SD",
            },
            {
                "P_TDATE": current_day,
                "P_TXTYPE": "SC",
            },
            {
                "P_TDATE": previous_day,
                "P_TYPE": "N",
                "P_TXTYPE": "SD",
            }
        ]
    }

    txs = collection.find(query, no_cursor_timeout=True)
    print 'TX num', txs.count()


def settle():
    uri = 'mongodb://ach:graduate@localhost:27017/ach'
    astar_mongo = MongoClient(uri)
    db = astar_mongo['ach']
    collection = db['transactions']

    previous_day = '01050623'
    current_day = '01050624'

    logging.basicConfig(
        filename='settle_{}_{}.log'.format(previous_day[-4:], current_day[-4:]),
        level=logging.DEBUG
    )

    query = {
        "$or": [
            {
                "P_TDATE": current_day,
                "P_TYPE": "R",
                "P_TXTYPE": "SD",
            },
            {
                "P_TDATE": current_day,
                "P_TXTYPE": "SC",
            },
            {
                "P_TDATE": previous_day,
                "P_TYPE": "N",
                "P_TXTYPE": "SD",
            }
        ]
    }

    txs = collection.find(query, no_cursor_timeout=True)
    print 'r size:', txs.count()
    count = 0
    bank_dict = {}
    print 'reset bank balance....'
    reset_all_bank_balance()

    start = time.time()

    mem_txs = []
    for tx in txs:
        mem_txs.append(tx)
    astar_mongo.close()

    for tx in mem_txs:
        # p_bank, r_bank, amount = tx
        p_bank = Bank.manager.get_bank_by_id(str(tx['P_PBANK'][:3]))
        r_bank = Bank.manager.get_bank_by_id(str(tx['P_RBANK'][:3]))
        amount = float(tx['P_AMT']) / BTC_NUM
        # signed_tx = pBank.send_to(rBank, float(tx['P_AMT'])/BTC_NUM, 2, 'pymongo yo')
        print '------------- COUNT: {} -------------'.format(count)

        if count % 1500 == 0:
            print 'Took {} seconds.'.format(time.time() - start)
            print 'BATCH EXEC...'
            for bank_id in Bank.manager.bank_list:
                bank = Bank.manager.get_bank_by_id(bank_id)
                tx_ids = bank.batch_execute()
                print bank.bank_id, ':', tx_ids
            print '[DONE] BATCH EXEC...'

        if count % 10000 == 0:
            print 'Took {} seconds.'.format(time.time() - start)
            print 'MERGING INPUTS...'
            for bank_id in Bank.manager.bank_list:
                bank = Bank.manager.get_bank_by_id(bank_id)
                bank.merge_tx_in(color=2, div=20)
            print '[DONE] MERGING INPUTS...'

        if count % 10000 == 0:
            logging.info('Tx count: {}'.format(count))
            logging.info('Took {} seconds.'.format(time.time() - start))

        print 'PBANK: {}, RBANK: {}, AMOUNT: {}'.format(p_bank.bank_id, r_bank.bank_id, amount)
        if tx['P_TDATE'] == previous_day:
            if tx['P_TYPE'] == 'N' and tx['P_TXTYPE'] == 'SD':
                count += 1
                r_bank.batch_send_to(p_bank, amount, 2, 'prev N SD')
                bank_dict[r_bank.bank_id] = bank_dict.get(r_bank.bank_id, 0) - amount * BTC_NUM
                bank_dict[p_bank.bank_id] = bank_dict.get(p_bank.bank_id, 0) + amount * BTC_NUM
        elif tx['P_TDATE'] == current_day:
            if tx['P_TXTYPE'] == 'SC':
                count += 1
                p_bank.batch_send_to(r_bank, amount, 2, 'current SC')
                bank_dict[r_bank.bank_id] = bank_dict.get(r_bank.bank_id, 0) + amount * BTC_NUM
                bank_dict[p_bank.bank_id] = bank_dict.get(p_bank.bank_id, 0) - amount * BTC_NUM
            elif tx['P_TYPE'] == 'R' and tx['P_TXTYPE'] == 'SD':
                count += 1
                r_bank.batch_send_to(p_bank, amount, 2, 'current R SD')
                bank_dict[r_bank.bank_id] = bank_dict.get(r_bank.bank_id, 0) - amount * BTC_NUM
                bank_dict[p_bank.bank_id] = bank_dict.get(p_bank.bank_id, 0) + amount * BTC_NUM

    print bank_dict
    print 'Took {} seconds.'.format(time.time() - start)
    logging.info('Tx count: {}'.format(count))
    logging.info('Took {} seconds.'.format(time.time() - start))
