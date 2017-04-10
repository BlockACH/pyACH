from flask import Flask, jsonify, request
from presenters import HistoryDataPresenter
from presenters import GcoinPresenter

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World!'

@app.route('/gcoin/alive', methods=['GET'])
def is_gcoin_alive():
    presenter = GcoinPresenter()
    return jsonify(data=presenter.is_gcoin_alive())

@app.route('/gcoin/clean', methods=['POST'])
def gcoin_clean():
    presenter = GcoinPresenter()
    return jsonify(data=presenter.clean_main_directory())

@app.route('/history-data/collect', methods=['GET'])
def history_data_collect():
    presenter = HistoryDataPresenter()
    return jsonify(data=presenter.collect_data())

@app.route('/history-data/pay', methods=['GET'])
def history_data_pay():
    presenter = HistoryDataPresenter()
    return jsonify(data=presenter.pay_data())

@app.route('/history-data/range', methods=['GET'])
def history_data_range():
    start_date = request.args.get('start', '')
    end_date = request.args.get('end', '')
    tx_type = request.args.get('txtype', '')
    presenter = HistoryDataPresenter()
    return jsonify(data=presenter.range_data(start_date, end_date))

@app.route('/settlement/db', methods=['GET'])
def db_settle():
    start_date = request.args.get('start', '')
    end_date = request.args.get('end', '')
    presenter = HistoryDataPresenter()
    return jsonify(data=presenter.db_settle(start_date, end_date))

@app.route('/bank/address', methods=['GET'])
def bank_address():
    presenter = HistoryDataPresenter()
    return jsonify(data=presenter.bank_address_dict())

@app.route('/transaction/trigger', methods=['GET', 'POST'])
def trigger():
    if request.method == 'POST':
        return jsonify(data=request.form)
    else:
        return jsonify(data={})
