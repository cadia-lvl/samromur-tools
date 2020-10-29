from tqdm import tqdm
import pandas as pd
from os.path import join, exists
from os import mkdir
from math import ceil
from json import dump

from training.normalize_samromur import normalize_sentence
from modules.MarosijoGenGraphs import genGraphs
from modules.MarosijoModule import MarosijoTask


def batch_loader(name, conf, ids_to_test=None):
    df = pd.read_csv(join(conf['metadata']), sep='\t', index_col='id')

    ids =[]
    recs_n = len(df)
    batch_size = conf['batch_size']

    print(f'\nThere are {recs_n} recordings in the metadata')
    if ids_to_test:
        ids = [int(id) for id in open(ids_to_test)]
        print(f"\nThere are {len(ids)} in the provided id's files")
        recs_n =len(ids)
    print(f"Creating {ceil(recs_n/batch_size)} batch/es")
    
    if not exists(conf['reports_path']):
        mkdir(conf['reports_path'])

    
    marosijo = MarosijoTask(False, conf['model'])
    if ids: 
        iter = ids
    else:   
        iter = df.index
    
    batch = []  
    recs=[]
    batch_counter=1
    for i in tqdm(iter, unit='lines'):
        sentence = normalize_sentence(df.at[i, 'sentence'])

        batch.append(f"{i}\t{sentence}")
        recs.append({"tokenId": i, 
                    "recPath": join(conf['recs'], df.at[i, 'filename']),
                    "recId": i,
                    "token": sentence,
                    "valid": 1})
        if i == 207:
            print(recs)
            
        if len(batch) == batch_size:
            print('Batch number: ', batch_counter)
            print('Creating graphs')

            genGraphs(batch)
            print('Created graphs')

            report = marosijo.processBatch(recs)
            print('Made a report')

            batch_name = name + '_' + str(batch_counter)
            write_report(report, conf, batch_name)
            
            store_ids(batch, conf, name)
            batch_counter+=1
            batch, recs = [], []


    if batch or recs:
        genGraphs(batch)
        report = marosijo.processBatch(recs)
        batch_name = name + '_' + str(batch_counter)
        write_report(report, conf, batch_name)


def write_report(report, conf, name):
    with open(join(conf['reports_path'], f"{name}.json"), 'w') as f_out:
        dump(report, ensure_ascii=False, fp=f_out, indent=4)

def store_ids(batch, conf, name):
    with open(join(conf['reports_path'], f"{name}_ids_done.txt"), 'a') as f_out:
        for line in batch:
            f_out.write(line.split('\t')[0]+'\n')