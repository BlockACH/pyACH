from bank import Bank

RESET_BALANCE = 1000  # in satoshi
CLEAN_COLOR = 2


def reset_bank_balance(bank):
    central_bank = Bank.manager.get_central_bank()
    balance = bank.balance
    diff = float(balance.get(2, 0) - RESET_BALANCE)

    if diff < 0:
        print 'CASE 1:', central_bank.send_to(bank, -1*diff, CLEAN_COLOR)
    elif diff > 0:
        print 'CASE 2:', bank.send_to(central_bank, diff, CLEAN_COLOR)

    if balance.get(1, 0) < 50:
        central_bank.send_to(bank, 1000, 1)

    print diff, bank.bank_id, bank.address, bank.balance


def main():
    print 'CB:', Bank.manager.get_central_bank().balance
    for bank_id in Bank.manager.bank_list:
        bank = Bank.manager.get_bank_by_id(bank_id)
        reset_bank_balance(bank)

if __name__ == '__main__':
    main()
