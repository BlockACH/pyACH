from flask import Blueprint, jsonify, request
from presenters import (
    HistoryDataPresenter, GcoinPresenter,
    NotificationPresenter, TransactionPresenter
)

settle = Blueprint('settle', __name__)


@settle.route('/')
def index():
    return 'Settle!'


@settle.route('/gcoin/alive', methods=['GET'])
def is_gcoin_alive():
    presenter = GcoinPresenter()
    return jsonify(data=presenter.is_gcoin_alive())


@settle.route('/gcoin/clean', methods=['POST'])
def gcoin_clean():
    presenter = GcoinPresenter()
    return jsonify(data=presenter.clean_main_directory())


@settle.route('/history-data/collect', methods=['GET'])
def history_data_collect():
    presenter = HistoryDataPresenter()
    return jsonify(data=presenter.collect_data())


@settle.route('/history-data/pay', methods=['GET'])
def history_data_pay():
    presenter = HistoryDataPresenter()
    return jsonify(data=presenter.pay_data())


@settle.route('/history-data/range', methods=['GET'])
def history_data_range():
    start_date = request.args.get('start', '')
    end_date = request.args.get('end', '')
    presenter = HistoryDataPresenter()
    return jsonify(data=presenter.range_data(start_date, end_date))


@settle.route('/settlement/db', methods=['GET'])
def db_settle():
    start_date = request.args.get('start', '')
    end_date = request.args.get('end', '')
    presenter = HistoryDataPresenter()
    return jsonify(data=presenter.db_settle(start_date, end_date))


@settle.route('/bank/address', methods=['GET'])
def bank_address():
    presenter = HistoryDataPresenter()
    return jsonify(data=presenter.bank_address_dict())


@settle.route('/transaction/trigger', methods=['GET', 'POST'])
def trigger():
    if request.method == 'POST':
        return jsonify(data=request.form)
    else:
        return jsonify(data={})


@settle.route('/transaction/query', methods=['GET'])
def query():
    trigger_bank = request.args.get('t', '')
    receive_bank = request.args.get('r', '')
    presenter = TransactionPresenter()
    txs = presenter.query(trigger_bank, receive_bank)
    return jsonify(data=txs)


@settle.route('/transaction/removeall', methods=['POST'])
def remove_all():
    presenter = TransactionPresenter()
    presenter.remove_all()
    return jsonify(data={'message': 'Deleted!'})


@settle.route('/notify', methods=['POST'])
def notify():
    data = request.json
    presenter = NotificationPresenter()
    key = presenter.notify(data)
    return jsonify(data={'key': key})
