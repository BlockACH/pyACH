BANK_LIST = [
    # banks for demo
    #'X', 'Y', 'Z', 'TCH',
    # banks from history data
    '6AB', 'A28', '46E', 'DD3', '822', 'CCC', '219',
    '18C', '170', 'B63', '62F', '5E0', '666', '519',
    'BA4', '5BD', '682', 'E07', 'B31', '0B1', 'FCB',
    'B89', '101', 'EDB', 'E75', '75D', 'A0D', '22D',
    'AB5', 'A1D', 'F73', 'C45', '481', '49A', 'EE0',
    '269', '7BA', '48C', 'E0C', 'CE3', '8DA', '552',
    '1F6', 'B30', '6D4', 'FB4', '4AD', '940', '838',
    'E15', 'F8E', '717', 'C72', '882', 'EA0'
]


class Contract(object):

    def init_state(self):
        state = {
            'unsettled_flow': {},
            'unsettled_balance': {b: 0 for b in BANK_LIST},
            'balance': {b: 0 for b in BANK_LIST}
        }

        for i in range(len(BANK_LIST)):
            for j in range(i+1, len(BANK_LIST)):
                state['unsettled_flow'][BANK_LIST[i]] = {}
                state['unsettled_flow'][BANK_LIST[j]] = {}

        for i in range(len(BANK_LIST)):
            for j in range(i+1, len(BANK_LIST)):
                state['unsettled_flow'][BANK_LIST[i]][BANK_LIST[j]] = 0
                state['unsettled_flow'][BANK_LIST[j]][BANK_LIST[i]] = 0

        return state

    def trade(self, data, state):
        state = dict(state)
        from_address = data['from_address']
        to_address = data['to_address']
        amount = data['amount']

        if state['balance'][from_address] >= amount:
            state['balance'][from_address] -= amount
            state['balance'][to_address] += amount
        else:
            state['unsettled_balance'][from_address] -= amount
            state['unsettled_balance'][to_address] += amount

            reverse_flow = state['unsettled_flow'][to_address][from_address]
            flow = amount - reverse_flow
            if flow > 0:
                state['unsettled_flow'][from_address][to_address] = flow
                state['unsettled_flow'][to_address][from_address] = 0
            else:
                state['unsettled_flow'][from_address][to_address] = 0
                state['unsettled_flow'][to_address][from_address] = -1 * flow
        return state

    def mint(self, data, state):
        state = dict(state)
        amount = data['amount']
        address = data['address']
        state['balance'][address] += amount
        return state

    def batch_settle(self, data, state):
        import copy

        state = dict(state)
        count = 0
        while True:
            old_state = copy.deepcopy(state)
            for bank_source in BANK_LIST:
                if (state['balance'][bank_source] > 0 and
                        state['unsettled_balance'][bank_source] < 0):
                    balance = state['balance'][bank_source]
                    for bank_to in BANK_LIST:
                        if bank_to == bank_source:
                            continue

                        if state['unsettled_flow'][bank_source][bank_to] > 0:
                            flow = state['unsettled_flow'][bank_source][bank_to]
                            diff = min(flow, balance)
                            state['unsettled_flow'][bank_source][bank_to] -= diff
                            state['unsettled_balance'][bank_source] += diff
                            state['unsettled_balance'][bank_to] -= diff
                            state['balance'][bank_source] -= diff
                            state['balance'][bank_to] += diff

                        if state['balance'][bank_source] == 0:
                            break
            if state == old_state:
                break
            count += 1
        return state

    def reset(self, data, state):
        return self.init_state()


def test(with_assert=True):
    import json

    contract = Contract()
    state = contract.init_state()

    trade_data = {'from_address': 'X', 'to_address': 'Y', 'amount': 5}
    state = contract.trade(trade_data, state)
    trade_data = {'from_address': 'Y', 'to_address': 'Z', 'amount': 3}
    state = contract.trade(trade_data, state)
    trade_data = {'from_address': 'Z', 'to_address': 'X', 'amount': 2}
    state = contract.trade(trade_data, state)
    if with_assert:
        assert state['unsettled_balance']['X'] == -3, 'wrong unsettled_balance'
        assert state['unsettled_balance']['Y'] == 2, 'wrong unsettled_balance'
        assert state['unsettled_balance']['Z'] == 1, 'wrong unsettled_balance'

    mint_data = {'address': 'X', 'amount': 3}
    state = contract.mint(mint_data, state)
    if with_assert:
        assert state['balance']['X'] == 3, '`mint` might not succeed'

    state = contract.batch_settle({}, state)
    if with_assert:
        assert state['balance']['X'] == 0, '`batch_settle` might not succeed'
        assert state['balance']['Y'] == 2, '`batch_settle` might not succeed'
        assert state['balance']['Z'] == 1, '`batch_settle` might not succeed'
        assert state['unsettled_balance']['X'] == 0, '`batch_settle` might not succeed'
        assert state['unsettled_balance']['Y'] == 0, '`batch_settle` might not succeed'
        assert state['unsettled_balance']['Z'] == 0, '`batch_settle` might not succeed'
        assert json.dumps(state)
    return state
