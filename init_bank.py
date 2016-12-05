from bank import Bank

RESET_BALANCE = 100000000000 # in satoshi

def reset_bank_balance(bank):
	print bank.balance


def main():
	for bank_id in Bank.manager.bank_list:
		bank = Bank.manager.get_bank_by_id(bank_id)
		import time
		time.sleep(0.1)
		reset_bank_balance(bank)

if __name__ == '__main__':
	main()