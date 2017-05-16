import os
import json
from config import SMART_CONTRACT_PATH


DEFAULT_CONTRACT_ID = 2


def create_reset_data(contract_id, comment=''):
    """
    Warning: This is only for conveniently reset data.
    Do not use in production
    """

    contract_data = {
        'type': 'RUN_CONTRACT',
        'contract_id': contract_id,
        'function': 'reset',
        'data': {},
        'comment': comment,
    }
    return json.dumps(contract_data)


def create_trade_data(from_address, to_address, amount, comment='',
                      contract_id=DEFAULT_CONTRACT_ID):
    contract_data = {
        'type': 'RUN_CONTRACT',
        'contract_id': contract_id,
        'function': 'trade',
        'data': {
            'from_address': from_address,
            'to_address': to_address,
            'amount': amount
        },
        'comment': comment,
    }
    return json.dumps(contract_data)


def create_mint_data(address, amount, comment='',
                     contract_id=DEFAULT_CONTRACT_ID, is_confidential=True):
    contract_data = {
        'type': 'RUN_CONTRACT',
        'contract_id': contract_id,
        'function': 'mint',
        'data': {'address': address, 'amount': amount},
        'comment': comment,
    }
    return json.dumps(contract_data)


def create_clear_queue_data(comment='', contract_id=DEFAULT_CONTRACT_ID):
    contract_data = {
        'type': 'RUN_CONTRACT',
        'contract_id': contract_id,
        'function': 'clear_queue',
        'data': {},
        'comment': comment,
    }
    return json.dumps(contract_data)


def create_deploy_data(contract_id=DEFAULT_CONTRACT_ID):
    ach_contract = os.path.join(SMART_CONTRACT_PATH, 'ACH_contract.py')
    with open(ach_contract, 'r') as f:
        contract_data = {
            'type': 'DEPLOY_CONTRACT',
            'contract_id': contract_id,
            'code': f.read(),
        }
    return json.dumps(contract_data)
