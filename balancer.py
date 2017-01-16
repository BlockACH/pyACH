import ast
#dynamic bnak_group
#dynamic end
def balancer(tx):
    """
    :type tx: dict
    :rtype group: int 
    """
    w = open("bank_group.json","r")
    bank_group = w.readline()
    bank_group = ast.literal_eval(bank_group)   

    p_bank = str(tx['P_PBANK'][:3])
    r_bank = str(tx['P_RBANK'][:3])
    bank = ""
    if tx['P_TYPE'] == 'N' and tx['P_TXTYPE'] == 'SD':
        bank = r_bank
    if tx['P_TXTYPE'] == 'SC':
        bank = p_bank    
    elif tx['P_TYPE'] == 'R' and tx['P_TXTYPE'] == 'SD':
        bank = r_bank
    return bank_group[bank]
