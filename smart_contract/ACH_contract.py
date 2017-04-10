BANK_LIST = [
    '6AB', 'A28', '46E', 'DD3', '822', 'CCC', '219',
    '18C', '170', 'B63', '62F', '5E0', '666', '519',
    'BA4', '5BD', '682', 'E07', 'B31', '0B1', 'FCB',
    'B89', '101', 'EDB', 'E75', '75D', 'A0D', '22D',
    'AB5', 'A1D', 'F73', 'C45', '481', '49A', 'EE0',
    '269', '7BA', '48C', 'E0C', 'CE3', '8DA', '552',
    '1F6', 'B30', '6D4', 'FB4', '4AD', '940', '838',
    'E15', 'F8E', '717', 'C72', '882', 'EA0', 'central_bank'
]


class Contract(object):

    def init_state(self):
        state = {
            'queue': [],
            'unsettled_balance': {b: 0 for b in BANK_LIST},
            'balance': {b: 0 for b in BANK_LIST}
        }
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
            state['queue'].append(data)
        return state

    def mint(self, data, state):
        state = dict(state)
        amount = data['amount']
        address = data['address']
        state['balance'][address] += amount
        return state

    def clear_queue(self, data, state):
        state = dict(state)
        remaining_queue = []
        for data in state['queue']:
            from_address = data['from_address']
            to_address = data['to_address']
            amount = data['amount']

            if state['balance'][from_address] >= amount:
                state['unsettled_balance'][from_address] += amount
                state['unsettled_balance'][to_address] -= amount
                state['balance'][from_address] -= amount
                state['balance'][to_address] += amount
            else:
                remaining_queue.append(data)

        state['queue'] = remaining_queue
        return state
