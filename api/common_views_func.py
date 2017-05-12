from flask import jsonify, request
from presenters import (
    BankPresenter,
    TransactionPresenter,
    TxStateChangePresenter,
    NotificationPresenter
)


def banks(bank_id, model):
    presenter = BankPresenter(bank_id, model)
    return jsonify(data=presenter.banks)


def query(bank_id, model):
    trigger_bank = request.args.get('t')
    receive_bank = request.args.get('r')
    status = request.args.get('s')
    presenter = TransactionPresenter(bank_id, model)
    txs = presenter.query(trigger_bank, receive_bank, status)
    return jsonify(data=txs)


def ready(bank_id, model):
    data = request.json
    presenter = TxStateChangePresenter(bank_id, model)
    tx_data = presenter.ready(data)
    return jsonify(data=tx_data)


def accept(bank_id, model):
    data = request.json
    presenter = TxStateChangePresenter(bank_id, model)
    tx_data = presenter.accept(data['key'])
    return jsonify(data=tx_data)


def reject(bank_id, model):
    data = request.json
    presenter = TxStateChangePresenter(bank_id, model)
    tx_data = presenter.reject(data['key'])
    return jsonify(data=tx_data)


def notify(bank_id, model):
    data = request.json
    presenter = NotificationPresenter(bank_id, model)
    key = presenter.notify(data)
    return jsonify(data={'key': key})
