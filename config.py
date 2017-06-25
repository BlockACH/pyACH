import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONTRACT_SERVER_URL = 'http://ach.csie.org:9999'

CLEAN_COLOR = 2
SMART_CONTRACT_ID = 1

SMART_CONTRACT_PATH = os.path.join(BASE_DIR, 'smart_contract')

DB_PATH = os.path.join(BASE_DIR, 'db')
SMART_CONTRACT_DB_PATH = os.path.join(DB_PATH, 'smart_contract')
SETTLE_DB_PATH = os.path.join(DB_PATH, 'settle')

GCOIN_RPC = {
    'user': 'boolafish',
    'password': 'abc123',
    'host': 'ach.csie.org',
    'port': '1125',
}

AUTHORIZED_BANKS = ['TCH', 'central_bank']

BANK_LIST = [
    # banks for demo
    'X', 'Y', 'Z',
    # banks from history data
    #'6AB', 'A28', '46E', 'DD3', '822', 'CCC', '219',
    #'18C', '170', 'B63', '62F', '5E0', '666', '519',
    #'BA4', '5BD', '682', 'E07', 'B31', '0B1', 'FCB',
    #'B89', '101', 'EDB', 'E75', '75D', 'A0D', '22D',
    #'AB5', 'A1D', 'F73', 'C45', '481', '49A', 'EE0',
    #'269', '7BA', '48C', 'E0C', 'CE3', '8DA', '552',
    #'1F6', 'B30', '6D4', 'FB4', '4AD', '940', '838',
    #'E15', 'F8E', '717', 'C72', '882', 'EA0'
]

BANK_URL = {
    'X': 'http://{}:{}'.format('localhost', '9877'),
    'Y': 'http://{}:{}'.format('localhost', '9877'),
    'Z': 'http://{}:{}'.format('localhost', '9877'),
    'TCH': 'http://{}:{}'.format('localhost', '9877'),
}

VALID_DATE_LIST = [
    '01050601', '01050602', '01050603', '01050604',
    '01050606', '01050607', '01050608', '01050613',
    '01050614', '01050615', '01050616', '01050617',
    '01050620', '01050621', '01050622', '01050623',
    '01050624', '01050627', '01050628', '01050629',
    '01050630', '01050701', '01050704', '01050705',
    '01050706', '01050707', '01050708', '01050711',
    '01050712', '01050713', '01050714', '01050715',
    '01050718', '01050719', '01050720', '01050721',
    '01050722', '01050725', '01050726', '01050727',
    '01050728', '01050729', '01050801', '01050802',
    '01050803', '01050804', '01050805', '01050808',
    '01050809', '01050810', '01050811', '01050812',
    '01050815', '01050816', '01050817', '01050818',
    '01050819', '01050822', '01050823', '01050824',
    '01050825', '01050826', '01050829', '01050830',
    '01050831'
]
