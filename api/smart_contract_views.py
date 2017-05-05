from flask import Blueprint, jsonify, request


smart_contract = Blueprint('smart_contract', __name__)


@smart_contract.route('/')
def index():
    return 'Smart Contract!'


@smart_contract.route('/transactions/trigger', methods=['POST'])
def trigger():
    print 'hi...', request.json
    return jsonify(data=request.json)
