from flask import Blueprint, jsonify, request
from presenters import (
    HistoryDataPresenter, GcoinPresenter,
    NotificationPresenter, TransactionPresenter
)

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


@settle.route('/<bank_id>/transaction/trigger', methods=['GET', 'POST'])
def trigger(bank_id):
    if request.method == 'POST':
        return jsonify(data=request.form)
    else:
        return jsonify(data={})


@settle.route('/<bank_id>/transaction/query', methods=['GET'])
def query(bank_id):
    trigger_bank = request.args.get('t', '')
    receive_bank = request.args.get('r', '')
    presenter = TransactionPresenter()
    txs = presenter.query(trigger_bank, receive_bank)
    return jsonify(data=txs)


@settle.route('/<bank_id>/transaction/removeall', methods=['POST'])
def remove_all(bank_id):
    presenter = TransactionPresenter()
    presenter.remove_all()
    return jsonify(data={'message': 'Deleted!'})


@settle.route('/<bank_id>/notify', methods=['POST'])
def notify(bank_id):
    data = request.json
    presenter = NotificationPresenter(bank_id, 'settle')
    key = presenter.notify(data)
    return jsonify(data={'key': key})
