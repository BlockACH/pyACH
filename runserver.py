import sys

from flask import Flask

from api.settle_views import settle
from api.smart_contract_views import smart_contract

app = Flask(__name__)
app.register_blueprint(settle, url_prefix='/settle')
app.register_blueprint(smart_contract, url_prefix='/smart_contract')

if len(sys.argv) > 1:
    port = int(sys.argv[1])
else:
    port = 8514

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
