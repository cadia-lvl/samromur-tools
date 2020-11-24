from tqdm import tqdm
import pandas as pd
from os.path import join, exists
from os import mkdir, remove
from math import ceil
import logging as log
from concurrent.futures import ProcessPoolExecutor
import shortuuid
import json

from config import conf
from training.normalize_samromur import normalize_sentence
from modules.MarosijoGenGraphs import genGraphs
from modules.MarosijoModule import MarosijoTask

log.basicConfig(level=log.ERROR,
    filename='log')

def batch_loader(args):
    '''
    Creates batches to review, the size of each batch can be change in config.py.
    Opens the metadata file for the samromur corpus and that is provided in config.py. 
    '''
    
    ids = get_ids(args.ids)
    df = pd.read_csv(join(conf['metadata']), sep='\t')
    df = df[df['id'].isin(ids)]
    df.set_index('id', inplace=True)
    data = []
    
    for i in df.index:
        sentence = normalize_sentence(df.at[i, 'sentence'])
        data.append({"tokenId": i, 
                    "recPath": join(conf['recs'], df.at[i, 'filename']),
                    "recId": i,
                    "token": sentence,
                    "valid": 1})
    batch_size=20
    #Hack for parallelzation
    data = [data[x:x+batch_size] for x in range(0, len(data), batch_size)]

    
    log.info(f"\nThere are {len(ids)} in the provided id's file")
    
    if not exists(conf['reports_path']):
        mkdir(conf['reports_path'])
    parallel_processor(create_and_decode, data, args.name, 6)

def parallel_processor(function, iterator, name, n_jobs, chunks=1, units ='files'):
    #Chunk size should be 1 in acordance with the hack above
    results: list = []
    with open(join(conf['reports_path'], f"{name}.json"), mode='w', encoding='utf-8' ) as f_out:
        f_out.write('[\n')
        with ProcessPoolExecutor(max_workers=n_jobs) as executor:
            results =  tqdm(executor.map(
                function,
                iterator,
                chunksize=chunks), 
                total=len(iterator),
                unit= ' '+ units)
            for chunk in results:
                if chunk:
                    for line in chunk:
                        json.dump(line, ensure_ascii=False, fp=f_out, indent=4)
                        f_out.write(',\n')
        f_out.write('{}]')

def create_and_decode(data:list):
    ''' 
    make this work the write
    '''
    u_prefix = shortuuid.uuid()

    graphs = [f"{r['recId']}\t{r['token']}" for r in data]
    genGraphs(graphs, u_prefix)
    
    marosijo = MarosijoTask(modelPath=conf['model'], u_prefix=u_prefix)
    report = marosijo.processBatch(data)
    
    remove(join('modules', 'local', 'temp', f'{u_prefix}_graphs.scp'))
    remove(join('modules', 'local', 'temp', f'{u_prefix}_graphs.ark'))
    
    return report

def create_and_decode1(data:list):
    '''
    make this work then write
    '''

    u_prefix = shortuuid.uuid()

    graphs = [f"{data['recId']}\t{data['token']}"]
    genGraphs(graphs, u_prefix)
    
    marosijo = MarosijoTask(modelPath=conf['model'], u_prefix=u_prefix)
    report = marosijo.processBatch([data])
    
    remove(join('modules', 'local', 'temp', f'{u_prefix}_graphs.scp'))
    remove(join('modules', 'local', 'temp', f'{u_prefix}_graphs.ark'))
    return report

def get_ids(path: str) -> list:
    '''
    Load a file with the ids to go over.
    The have to be present in the metadata file
    which is in provided through config.py
    '''
    items =[]
    with open(path) as f_in:
        for line in f_in:
            items.append(int(line))
    return items
