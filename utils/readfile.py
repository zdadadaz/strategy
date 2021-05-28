import pandas as pd

def read_strat_res(path_to_strat):
    with open(path_to_strat, 'r') as f:
        contents = f.readlines()
    
    ticker = path_to_strat.split('.')[-2].split('/')[-1]
    profit = None
    for line in contents:
        tmp = line.strip().split("\t")
        if len(tmp)>2 and tmp[1] == 'start':
            profit = float(tmp[-1][:-1])
    return (profit, ticker) if profit else None