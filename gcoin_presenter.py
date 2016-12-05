import gcoin
from gcoinrpc import connect_to_remote
from config import GCOIN_RPC, BANK_LIST


def get_rpc_connection():
    return connect_to_remote(GCOIN_RPC['user'],
                             GCOIN_RPC['password'],
                             GCOIN_RPC['host'],
                             GCOIN_RPC['port'])


def balance_from_utxos(utxos):
    balance_dict = {}
    if utxos:
        for utxo in utxos:
            color = utxo['color']
            value = utxo['value']
            balance_dict[color] = balance_dict.get(color, 0) + value
    return balance_dict


def select_utxo(utxos, color, sum, exclude=[]):
    if not utxos:
        return []

    utxos = [utxo for utxo in utxos if utxo['color'] == color and utxo not in exclude]
    utxos = sorted(utxos, key=lambda utxo: utxo['value'])

    value = 0
    for i, utxo in enumerate(utxos):
        value += utxo['value']
        if value >= sum:
            return utxos[:i + 1]
    return []


def utxo_to_txin(utxo):
    return {
        'tx_id': utxo['txid'],
        'index': utxo['vout'],
        'script': utxo['scriptPubKey']
    }


class GcoinPresenter(object):

    def __init__(self):
        self.rpc_conn = get_rpc_connection()

    def get_address_balance(self, address):
        utxos = self.rpc_conn.gettxoutaddress(address)
        return balance_from_utxos(utxos)

    def send_raw_tx(self, raw_tx):
        return self.rpc_conn.sendrawtransaction(raw_tx)

    def create_raw_tx(self, address_from, address_to, amount, color, comment=''):
        utxos = self.rpc_conn.gettxoutaddress(address_from)

        if color != 1:
            inputs = select_utxo(utxos=utxos, color=color, sum=amount)
            fee_inputs = select_utxo(utxos=utxos, color=1, sum=1, exclude=inputs)
            inputs.extend(fee_inputs)
        else:
            inputs = select_utxo(utxos=utxos, color=color, sum=amount + 1)

        if not inputs:
            raise Exception('not enough balance')

        outs = [{
            'address': address_to,
            'value': int(amount * 10**8),
            'color': color
        }]

        inputs_balance = balance_from_utxos(inputs)
        for input_color in inputs_balance:
            change_amount = inputs_balance[input_color]
            if input_color == color:
                change_amount -= amount
            if input_color == 1:
                change_amount -= 1
            if change_amount:
                outs.append({
                    'address': address_from,
                    'value': int(change_amount * 10**8),
                    'color': input_color
                })

        tx_type = 0
        if comment:
            outs.append({
                'script': gcoin.mk_op_return_script(comment.encode('utf8')),
                'value': 0,
                'color': 0
            })
            tx_type = 5

        ins = [utxo_to_txin(utxo) for utxo in inputs]
        return gcoin.make_raw_tx(ins, outs, tx_type)
