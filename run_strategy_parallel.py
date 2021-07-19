import pandas as pd
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
import copy
from utils import strategy
from utils import readfile as rf
from utils import writefile as wf
from datetime import date
import os

def summary(path_to_dir, path_to_out):
    filelist = []
    for path, subdirs, files in os.walk(path_to_dir):
        for name in files:
            if name[0] != '.' and name.split('.')[-1] == 'txt':
                tmp = rf.read_strat_res(os.path.join(path, name))
                if tmp:
                    filelist.append(tmp)
    filelist.sort(reverse=True)
    wf.write_to_csv(path_to_out+'.csv', filelist)

def main():
    path_to_out = 'strategy_out/summary_{}'.format(date.today())
    # input data
    df = pd.read_csv('datas/TW50.csv')
    instruments = list(df['ticker'])
    split = cpu_count() - 1
    path_to_dir = f'strategy_out/{date.today()}'
    print("cpu {} and split {}".format(cpu_count(), split))
   

    n = len(instruments)
    arr = list(zip(copy.deepcopy(instruments), ['up' for i in range(n)]))
    arr += list(zip(copy.deepcopy(instruments), ['down' for i in range(n)]))
    arr += list(zip(copy.deepcopy(instruments), ['all' for i in range(n)]))

    # for a in arr:
    #     if a[0] == 2382:
    #         strategy.strategy_fn(a)

    pool = Pool(processes=split)
    pool.map(strategy.strategy_fn, arr)
    pool.close()
    summary(path_to_dir, path_to_out)

if __name__ == '__main__':
    main()
