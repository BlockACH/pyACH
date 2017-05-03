import plyvel
import json

db = plyvel.DB('/tmp/testdb/', create_if_missing=True)

db.put(b'fuck', b'song')
demo_txs = [
    {
        'status': 'trigger',
        'pbank': 'XYZ',
        'rbank': 'XXX',
        'amount': 1200,
    },
    {
        'status': 'receive',
        'pbank': 'XYZ',
        'rbank': 'XXX',
        'amount': 3700,
    },
    {
        'status': 'unconfirm',
        'pbank': 'YYY',
        'rbank': 'XXX',
        'amount': 2340,
    },
    {
        'status': 'confirmed',
        'pbank': 'XXX',
        'rbank': 'ZZZ',
        'amount': 8460,
    }
]

db.put('demo_txs', json.dumps(demo_txs))
print db.get(b'demo_txs')
print db.get(b'fuck')
load_data = json.loads(db.get('demo_txs'))

for b in load_data:
    b['status'] = 'fuck'

db.put('demo_txs', json.dumps(load_data))
print db.get(b'demo_txs')
