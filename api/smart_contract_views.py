from flask import Blueprint, jsonify, request
from presenters import (
    TxStateChangePresenter, NotificationPresenter,
    TransactionPresenter
)

SMART_CONTRACT_MODEL = 'smart_contract'

smart_contract = Blueprint('smart_contract', __name__)


@smart_contract.route('/')
def index():
    return 'Smart Contract!'


@smart_contract.route('/notify', methods=['POST'])
def notify():
    bank_id = request.args.get('bank_id', '')
    data = request.json
    presenter = NotificationPresenter(bank_id, SMART_CONTRACT_MODEL)
    key = presenter.notify(data)
    return jsonify(data={'key': key})


@smart_contract.route('/transaction/query', methods=['GET'])
def query():
    bank_id = request.args.get('bank_id', '')
    trigger_bank = request.args.get('t', '')
    receive_bank = request.args.get('r', '')
    presenter = TransactionPresenter(bank_id, SMART_CONTRACT_MODEL)
    txs = presenter.query(trigger_bank, receive_bank)
    return jsonify(data=txs)


@smart_contract.route('/transaction/ready', methods=['POST'])
def ready():
    bank_id = request.args.get('bank_id', '')
    data = request.json
    presenter = TxStateChangePresenter(bank_id, SMART_CONTRACT_MODEL)
    tx_data = presenter.ready(data)
    return jsonify(data=tx_data)


@smart_contract.route('/transaction/accept', methods=['POST'])
def accept():
    bank_id = request.args.get('bank_id', '')
    data = request.json
    presenter = TxStateChangePresenter(bank_id, SMART_CONTRACT_MODEL)
    tx_data = presenter.accept(data['key'])
    return jsonify(data=tx_data)


@smart_contract.route('/transaction/reject', methods=['POST'])
def reject():
    bank_id = request.args.get('bank_id', '')
    data = request.json
    presenter = TxStateChangePresenter(bank_id, SMART_CONTRACT_MODEL)
    tx_data = presenter.reject(data['key'])
    return jsonify(data=tx_data)
