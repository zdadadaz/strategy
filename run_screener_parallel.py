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
    for fn in range(num):
        df = pd.read_csv(path_to_csv + '_{}'.format(fn) + '.csv', index_col=None, header=0)
        dfs.append(df)
    frame = pd.concat(dfs, axis=0, ignore_index=True)
    frame.to_csv(path_to_csv + '.csv', index = False)
    os.system('rm {}'.format(path_to_csv + "_*.csv"))


def main():
    #Add data to Cerebro
    # instruments = ['2303.TW', '2330.TW', '2454.TW', '3034.TW']
    path_to_csv = 'screen_out/{}'.format(date.today())
    df = pd.read_csv('datas/TW50.csv')
    filelist = list(df['ticker'])
    split = cpu_count() - 1
    print("have cpu {} and split {}".format(cpu_count(), split) )
    arr = []
    step = len(filelist) // split
    for i in range(split):
        if i == split - 1:
            arr.append((filelist[(step * i):], i))
        else:
            arr.append((filelist[(step * i):(step * (i + 1))], i))
    screener.screener_fn(arr[0])
    pool = Pool(processes=split)
    pool.map(screener.screener_fn, arr)
    pool.close()
    concat_csv(path_to_csv, split)
    os.system('cp -f screen_out/{}.csv ../dash/screener/{}.csv'.format(date.today(), date.today()))

if __name__ == '__main__':
    main()