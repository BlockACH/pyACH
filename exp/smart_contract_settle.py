import time

from exp.init_bank import init_bank as gcoin_bank_init
from pymongo import MongoClient
from bank import Bank

CONTRACT_ID = 1


def init_bank():
    c = Bank.manager.get_central_bank()
    c.reset_contract(contract_id=CONTRACT_ID)

    print 'clear bank balance to zero....'
    for bank_id in Bank.manager.bank_list:
        bank = Bank.manager.get_bank_by_id(bank_id)
        initial_amount = 1000000
        print 'mint for bank {}'.format(bank_id)
        bank.contract_mint(initial_amount, contract_id=CONTRACT_ID)


def send_tx():
    print 'send tx......'
    Bank.manager.send_pool_txs()


def settle():
    print 'deploy contract...'
    central_bank = Bank.manager.get_central_bank()
    central_bank.deploy_contract(contract_id=CONTRACT_ID)

    init_bank()

    uri = 'mongodb://ach:graduate@localhost:27017/ach'
    astar_mongo = MongoClient(uri)
    db = astar_mongo['ach']
    collection = db['transactions']

    previous_day = '010506020'
    current_day = '01050621'

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
        amount = float(tx['P_AMT'])

        p_bank = Bank.manager.get_bank_by_id(str(tx['P_PBANK'][:3]))
        r_bank = Bank.manager.get_bank_by_id(str(tx['P_RBANK'][:3]))

        if count % 1000 == 0:
            print '------------- COUNT: {} -------------'.format(count)
            print 'Took {} seconds.'.format(time.time() - start)
            if count > 0:
                for bank_id in Bank.manager.bank_list:
                    bank = Bank.manager.get_bank_by_id(bank_id)
                    initial_amount = 1000000
                    bank.contract_mint(initial_amount, contract_id=CONTRACT_ID)
                c = Bank.manager.get_central_bank()
                c.contract_clear_queue(contract_id=CONTRACT_ID)
            print '------------- DONE -------------'

        valid = True
        if tx['P_TDATE'] == previous_day:
            if tx['P_TYPE'] == 'N' and tx['P_TXTYPE'] == 'SD':
                bank_dict[r_bank.bank_id] = bank_dict.get(r_bank.bank_id, 0) - amount
                bank_dict[p_bank.bank_id] = bank_dict.get(p_bank.bank_id, 0) + amount
                r_bank.contract_send_to(p_bank, amount,
                                        contract_id=CONTRACT_ID,
                                        comment=str(count))
            else:
                valid = False
        elif tx['P_TDATE'] == current_day:
            if tx['P_TXTYPE'] == 'SC':
                bank_dict[r_bank.bank_id] = bank_dict.get(r_bank.bank_id, 0) + amount
                bank_dict[p_bank.bank_id] = bank_dict.get(p_bank.bank_id, 0) - amount
                p_bank.contract_send_to(r_bank, amount,
                                        contract_id=CONTRACT_ID,
                                        comment=str(count))
            elif tx['P_TYPE'] == 'R' and tx['P_TXTYPE'] == 'SD':
                bank_dict[r_bank.bank_id] = bank_dict.get(r_bank.bank_id, 0) - amount
                bank_dict[p_bank.bank_id] = bank_dict.get(p_bank.bank_id, 0) + amount
                r_bank.contract_send_to(p_bank, amount,
                                        contract_id=CONTRACT_ID,
                                        comment=str(count))
            else:
                valid = False
        else:
            valid = False

        if valid:
            print 'PBANK: {pbank}, RBANK: {rbank}, AMOUNT: {amount}'.format(
                pbank=p_bank.bank_id,
                rbank=r_bank.bank_id,
                amount=amount
            )
            count += 1

    print bank_dict
    astar_mongo.close()
