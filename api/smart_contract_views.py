from flask import Blueprint, jsonify, request
from presenters import TriggerPresenter, NotificationPresenter

smart_contract = Blueprint('smart_contract', __name__)


@smart_contract.route('/')
def index():
    return 'Smart Contract!'


@smart_contract.route('/notify', methods=['POST'])
def notify():
    bank_id = request.args.get('bank_id', '')
    data = request.json
    presenter = NotificationPresenter(bank_id, 'smart_contract')
    key = presenter.notify(data)
    return jsonify(data={'key': key})


@smart_contract.route('/trigger', methods=['POST'])
def trigger():
    bank_id = request.args.get('bank_id', '')
    data = request.json
    presenter = TriggerPresenter(bank_id, 'smart_contract')
    presenter.trigger(data)
    return jsonify(data=data)
