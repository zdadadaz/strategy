
def write_to_csv(path_to_csv, out):
    with open(path_to_csv, 'w') as f:
        f.write("")
    
    with open(path_to_csv, '+a') as f:
        f.write("type,ticker,profit\n")
        for i in out:
            f.write("{},{},{}\n".format('_'.join(i[1].split('_')[:-1]), i[1].split('_')[-1], i[0]))
    