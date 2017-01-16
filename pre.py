from pymongo import MongoClient
from config import  BANK_LIST, BTC_NUM, ASTAR_MONGO_URI

def get_bank_tx_count():
    '''
        input :
        output : bank_count.json (each bank's txs count)  
    '''
    astar_mongo = MongoClient(ASTAR_MONGO_URI)
    db = astar_mongo['ach']
    collection = db['txs']
    
    txs_count = {}
    txs =collection.find()
    count = 0 
    
    for i in BANK_LIST:
        txs_count[i] = 0
    
    for tx in txs:
        count += 1
        r = str(tx['P_PBANK'][:3])
        p = str(tx['P_RBANK'][:3])
        if r not in BANK_LIST:
            r = 'EA0'
        if p not in BANK_LIST:
            p = 'EA0'
        if tx['P_TYPE'] == 'N' and tx['P_TXTYPE'] == 'SD':
            txs_count[r] += 1 
        if tx['P_TXTYPE'] == 'SC':
            txs_count[p] += 1 
        elif tx['P_TYPE'] == 'R' and tx['P_TXTYPE'] == 'SD':
            txs_count[r] += 1 
        if count%5000 == 0 :
             print '------------- COUNT: {} -------------'.format(count)
    w = open("txs_count.json","w")
    w.write(str(txs_count))
    return txs_count
    
def get_bank_group(N, txs_count) :
    ''' 
        input       : size of group (int), txs_count.json  
        generator   : bank_group.json
    '''    
    #w = open("txs_count.json","r")
    #txs_count = w.readline()
    #txs_count = ast.literal_eval(txs_count)
    #w.close()

    #To smooth the zero count
    for i in txs_count:
        txs_count[i] += 1

    group_count = {}
    for i in range(0,N):
        group_count[i] = 0 
    
    bank_group = {}
    for i in txs_count:
        bank_group[i] = 0 
    
    for i in txs_count:
        min_group = 0 
        for j in group_count:
            if group_count[min_group] > group_count[j]:
                min_group = j 
        bank_group[i] = min_group
        group_count[min_group] += txs_count[i]
    
    w = open("bank_group.json","w")
    w.write(str(bank_group)) 
    
    dynamic_gp ="bank_group = {\n"
    for i in bank_group:
       dynamic_gp = dynamic_gp + '\t"' + i + '" : ' + str(bank_group[i]) + ",\n"
    dynamic_gp += "}\n"
    
    y = open("balancer.py","r")
    balancer_py = y.readlines()
    balancer_py_update = []
    deal_dynamic = False
    for i in balancer_py :
        if i == "#dynamic end\n":
            deal_dynamic = False
        if  not deal_dynamic:
            balancer_py_update.append(i)
        if i == "#dynamic bnak_group\n":
            balancer_py_update.append(dynamic_gp)
            deal_dynamic = True
        
    y.close()
    
    y = open("balancer.py","w")
    for i in balancer_py_update :
        y.write(i)

if __name__ == "__main__" :
    txs_count = get_bank_tx_count()
    get_bank_group(4, txs_count)
