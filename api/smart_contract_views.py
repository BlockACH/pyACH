from flask import Blueprint, jsonify, request
from presenters import BatchSettlePresenter, SmartContractMintPresenter
from common_views_func import (
    query, ready, accept, reject, notify, banks
)

SMART_CONTRACT_MODEL = 'smart_contract'

smart_contract = Blueprint('smart_contract', __name__)


@smart_contract.route('/')
def index():
    return 'Smart Contract!'


@smart_contract.route('/<bank_id>/batch_settle', methods=['POST'])
def batch_settle(bank_id):
    if bank_id == 'TCH':
        presenter = BatchSettlePresenter()
        txid = presenter.batch_settle()
        return jsonify(data=txid)
    return jsonify({'error': 'unauthorized'})


@smart_contract.route('/<bank_id>/mint', methods=['POST'])
def mint(bank_id):
    if bank_id == 'TCH':
        data = request.json
        presenter = SmartContractMintPresenter()
        txid = presenter.mint(data['bank'], data['amount'])
        return jsonify(data=txid)
    return jsonify({'error': 'unauthorized'})


@smart_contract.route('/<bank_id>/banks', methods=['GET'])
def smart_contract_banks(bank_id):
    return banks(bank_id, SMART_CONTRACT_MODEL)


@smart_contract.route('/<bank_id>/transactions/notify', methods=['POST'])
def smart_contract_notify(bank_id):
    return notify(bank_id, SMART_CONTRACT_MODEL)


@smart_contract.route('/<bank_id>/transactions/query', methods=['GET'])
def smart_contract_query(bank_id):
    return query(bank_id, SMART_CONTRACT_MODEL)


@smart_contract.route('/<bank_id>/transactions/ready', methods=['POST'])
def smart_contract_ready(bank_id):
    return ready(bank_id, SMART_CONTRACT_MODEL)


@smart_contract.route('/<bank_id>/transactions/accept', methods=['POST'])
def smart_contract_accept(bank_id):
    return accept(bank_id, SMART_CONTRACT_MODEL)


@smart_contract.route('/<bank_id>/transactions/reject', methods=['POST'])
def smart_contract_reject(bank_id):
    return reject(bank_id, SMART_CONTRACT_MODEL)
