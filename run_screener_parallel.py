import datetime
import pandas as pd
from tqdm import tqdm
from datetime import date
import os
from multiprocessing import Pool, cpu_count
import copy
from utils import screener

def concat_csv(path_to_csv, num):
    dfs = []
    subfile = path_to_csv[:-3]
    for fn in range(num):
        df = pd.read_csv(f'{subfile}' + '_{}'.format(fn) + '.csv', index_col=None, header=0)
        dfs.append(df)
    frame = pd.concat(dfs, axis=0, ignore_index=True)
    for i in range(num):
        os.system('rm {}'.format(f'{subfile}' + f"_{i}.csv"))
    frame.to_csv(path_to_csv + '.csv', index = False)


def main():
    #Add data to Cerebro
    # instruments = ['2303.TW', '2330.TW', '2454.TW', '3034.TW']
    suffix = 'AX'
    if suffix=='AX':
        df = pd.read_csv('datas/AU300.csv')
        path_to_csv = 'screen_out/{}_{}'.format(date.today(),suffix)
    else:
        df = pd.read_csv('datas/TW50.csv')
        path_to_csv = 'screen_out/{}_{}'.format(date.today(),suffix)
    filelist = list(df['ticker'])
    split = cpu_count() - 1
    print("have cpu {} and split {}".format(cpu_count(), split) )
    arr = []
    step = len(filelist) // split
    for i in range(split):
        if i == split - 1:
            arr.append((filelist[(step * i):], i, suffix))
        else:
            arr.append((filelist[(step * i):(step * (i + 1))], i, suffix))
    # screener.screener_fn(arr[0])
    pool = Pool(processes=split)
    pool.map(screener.screener_fn, arr)
    pool.close()
    concat_csv(path_to_csv, split)
    os.system('cp -f screen_out/{}_{}.csv ../dash/screener/{}.csv'.format(date.today(),suffix, date.today()))

if __name__ == '__main__':
    main()