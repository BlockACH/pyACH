import sys

from flask import Flask, url_for, jsonify

from api.settle_views import settle
from api.smart_contract_views import smart_contract

app = Flask(__name__)
app.register_blueprint(settle, url_prefix='/settle')
app.register_blueprint(smart_contract, url_prefix='/smart_contract')


@app.route('/')
def list_routes():
    import urllib
    output = []
    for rule in app.url_map.iter_rules():

        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        line = urllib.unquote("{:50s} {:20s} {}".format(
            rule.endpoint, methods, url
        ))
        output.append(line)

    for line in sorted(output):
        print line
    return jsonify(data=output)


if len(sys.argv) > 1:
    port = int(sys.argv[1])
else:
    port = 8514

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)
