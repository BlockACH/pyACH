from flask import Flask, jsonify, request

from presenters import HistoryDataPresenter

app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello World!'


@app.route('/history-data/collect', methods=['GET'])
def history_data_collect():
    presenter = HistoryDataPresenter()
    return jsonify(data=presenter.collect_data())


@app.route('/history-data/pay', methods=['GET'])
def history_data_pay():
    presenter = HistoryDataPresenter()
    return jsonify(data=presenter.pay_data())


@app.route('/transaction/trigger', methods=['GET', 'POST'])
def trigger():
    if request.method == 'POST':
        return jsonify(data=request.form)
    else:
        return jsonify(data={})
