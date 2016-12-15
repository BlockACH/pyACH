import gcoin
from decimal import Decimal
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

    def merge_tx_in(self, address, color, priv, div=50):
        if color == 1:
            raise Exception('Not support to merge color 1')

        utxos = self.rpc_conn.gettxoutaddress(address)
        color_utxos = [] if not utxos else [utxo for utxo in utxos if utxo['color'] == color]

        while len(color_utxos) > div:
            print 'REMAINING {} txins....'.format(len(color_utxos))
            inputs = color_utxos[0:div]
            fee_inputs = select_utxo(utxos=utxos, color=1, sum=1, exclude=inputs)
            inputs.extend(fee_inputs)
            inputs_balance = balance_from_utxos(inputs)
            outs = []
            for input_color in inputs_balance:
                change_amount = Decimal(str(inputs_balance[input_color]))

                if input_color == 1:
                    change_amount = change_amount - 1

                if change_amount:
                    outs.append({
                        'address': address,
                        'value': int(change_amount * 10**8),
                        'color': input_color
                    })
            ins = [utxo_to_txin(utxo) for utxo in inputs]
            raw_tx = gcoin.make_raw_tx(ins, outs)
            signed_tx = gcoin.signall(raw_tx, priv, parallel=True)
            self.send_raw_tx(signed_tx)
            utxos = self.rpc_conn.gettxoutaddress(address)
            color_utxos = [utxo for utxo in utxos if utxo['color'] == color]

    def create_raw_tx(self, address_from, address_to, amount, color, comment=''):
        utxos = self.rpc_conn.gettxoutaddress(address_from)

        if color != 1:
            inputs = select_utxo(utxos=utxos, color=color, sum=amount)
            fee_inputs = select_utxo(utxos=utxos, color=1, sum=1, exclude=inputs)
            if not inputs:
                raise Exception('not enough balance')
            if not fee_inputs:
                raise Exception('not enough fee balance')
            inputs.extend(fee_inputs)
        else:
            inputs = select_utxo(utxos=utxos, color=color, sum=amount + 1)
            if not inputs:
                raise Exception('not enough balance')

        outs = [{
            'address': address_to,
            'value': int(Decimal(str(amount)) * 10**8),
            'color': color
        }]

        inputs_balance = balance_from_utxos(inputs)
        for input_color in inputs_balance:
            change_amount = Decimal(str(inputs_balance[input_color]))

            if input_color == color:
                change_amount = change_amount - Decimal(str(amount))

            if input_color == 1:
                change_amount = change_amount - 1

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

    def create_license(self, address, color):
        license = {
            'name': 'name',
            'description': 'description',
            'issuer': 'none',
            'fee_collector': 'none',
            'member_control': False,
            'metadata_link': 'www.www.com',
            'upper_limit': 0,
        }

        license_hex = gcoin.encode_license(license)
        return self.rpc_conn.sendlicensetoaddress(address, color, license_hex)

    def mint(self, amount, color):
        return self.rpc_conn.mint(amount, color)

    def send_to_address(self, address, amount, color):
        return self.rpc_conn.sendtoaddress(address, amount, color)

    def get_fixed_address(self):
        return self.rpc_conn.proxy.getfixedaddress()

    def is_license_exist(self, color):
        try:
            self.rpc_conn.getlicenseinfo(color)
        except Exception:
            return False
        else:
            return True
