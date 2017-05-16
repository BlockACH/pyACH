from flask import Blueprint, jsonify, request
from presenters import (
    HistoryDataPresenter, GcoinPresenter,
    TransactionPresenter, TxStateChangePresenter
)
from common_views_func import (
    query, ready, accept, reject, notify, banks, removeall
)


SETTLE_MODEL = 'settle'
settle = Blueprint('settle', __name__)


@settle.route('/')
def index():
    return 'Settle!'


@settle.route('/<bank_id>/gcoin/alive', methods=['GET'])
def is_gcoin_alive(bank_id):
    presenter = GcoinPresenter()
    return jsonify(data=presenter.is_gcoin_alive())


@settle.route('/<bank_id>/gcoin/clean', methods=['POST'])
def gcoin_clean(bank_id):
    presenter = GcoinPresenter()
    return jsonify(data=presenter.clean_main_directory())


@settle.route('/<bank_id>/history-data/collect', methods=['GET'])
def history_data_collect(bank_id):
    presenter = HistoryDataPresenter()
    return jsonify(data=presenter.collect_data())


@settle.route('/<bank_id>/history-data/pay', methods=['GET'])
def history_data_pay(bank_id):
    presenter = HistoryDataPresenter()
    return jsonify(data=presenter.pay_data())


@settle.route('/<bank_id>/history-data/range', methods=['GET'])
def history_data_range(bank_id):
    start_date = request.args.get('start', '')
    end_date = request.args.get('end', '')
    presenter = HistoryDataPresenter()
    return jsonify(data=presenter.range_data(start_date, end_date))


@settle.route('/<bank_id>/settlement/db', methods=['GET'])
def db_settle(bank_id):
    start_date = request.args.get('start', '')
    end_date = request.args.get('end', '')
    presenter = HistoryDataPresenter()
    return jsonify(data=presenter.db_settle(start_date, end_date))


@settle.route('/<bank_id>/bank/address', methods=['GET'])
def bank_address(bank_id):
    presenter = HistoryDataPresenter()
    return jsonify(data=presenter.bank_address_dict())


@settle.route('/<bank_id>/transactions/removeall', methods=['POST'])
def remove_all(bank_id):
    return removeall(bank_id, SETTLE_MODEL)


@settle.route('/<bank_id>/banks')
def settle_banks(bank_id):
    return banks(bank_id, SETTLE_MODEL)


@settle.route('/<bank_id>/transactions/query', methods=['GET'])
def settle_query(bank_id):
    return query(bank_id, SETTLE_MODEL)


@settle.route('/<bank_id>/transactions/notify', methods=['POST'])
def settle_notify(bank_id):
    return notify(bank_id, SETTLE_MODEL)


@settle.route('/<bank_id>/transactions/ready', methods=['POST'])
def settle_ready(bank_id):
    return ready(bank_id, SETTLE_MODEL)


@settle.route('/<bank_id>/transactions/accept', methods=['POST'])
def settle_accept(bank_id):
    return accept(bank_id, SETTLE_MODEL)


@settle.route('/<bank_id>/transactions/reject', methods=['POST'])
def settle_reject(bank_id):
    return reject(bank_id, SETTLE_MODEL)


@settle.route('/<bank_id>/transactions/approve', methods=['POST'])
def settle_approve(bank_id):
    data = request.json
    presenter = TxStateChangePresenter(bank_id, SETTLE_MODEL)
    tx_data = presenter.approve(data['key'])
    return jsonify(data=tx_data)


@settle.route('/<bank_id>/transactions/destroy', methods=['POST'])
def settle_destroy(bank_id):
    data = request.json
    presenter = TxStateChangePresenter(bank_id, SETTLE_MODEL)
    tx_data = presenter.destroy(data['key'])
    return jsonify(data=tx_data)
