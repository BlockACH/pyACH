from flask import Blueprint, jsonify, request
from presenters import TriggerPresenter, NotificationPresenter

smart_contract = Blueprint('smart_contract', __name__)


@smart_contract.route('/')
def index():
    return 'Smart Contract!'


@smart_contract.route('/notify', methods=['POST'])
def notify():
    data = request.json
    presenter = NotificationPresenter('smart_contract')
    key = presenter.notify(data)
    return jsonify(data={'key': key})


@smart_contract.route('/trigger', methods=['POST'])
def trigger():
    data = request.json
    presenter = TriggerPresenter('smart_contract')
    presenter.trigger(data)
    return jsonify(data=data)
