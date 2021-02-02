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
from modules.MarosijoGenGraphs import genGraphs
from modules.MarosijoModule import MarosijoTask

log.basicConfig(level=log.ERROR,
    filename='log/log')

def batch_loader1(args):
    '''
    Creates batches to review, the size of each batch can be change in config.py.
    Opens the metadata file for the samromur corpus and that is provided in config.py. 
    '''
    
    ids = get_ids(args.ids)
    df = pd.read_csv(join(conf['metadata']), sep='\t', dtype='str')
    df = df[df['id'].isin(ids)]
    df.set_index('id', inplace=True)
    data = []
    
    for i in df.index:
        sentence = df.at[i, 'sentence_norm']
        data.append({"tokenId": i, 
                    "recPath": join(conf['recs'], df.at[i, 'filename']),
                    "recId": i,
                    "token": sentence,
                    "valid": df.at[i, 'is_valid']})

    #Hack for parallelzation
    data = [data[x:x+args.batch_size] for x in range(0, len(data), args.batch_size)]

    for batch in data:
        print(len(batch))

    log.info(f"\nThere are {len(ids)} in the provided id's file")
    
    if not exists(conf['reports_path']):
        mkdir(conf['reports_path'])

    with open(join(conf['reports_path'], f"{args.name}.json"), mode='w', encoding='utf-8' ) as f_out:
        f_out.write('[\n')
        for batch in data:
            batch_name = shortuuid.uuid()

            #Graphs á að vera listi strengur með <tokenID>\t<token>
            graphs = [f"{line['recId']}\t{line['token']}" for line in batch]
            genGraphs(graphs, batch_name)

            marosijo = MarosijoTask(modelPath=conf['model'], u_prefix=batch_name)
            
            report = marosijo.processBatch(batch)

            remove(join('modules', 'local', 'temp', f'{batch_name}_graphs.scp'))
            remove(join('modules', 'local', 'temp', f'{batch_name}_graphs.ark'))

            json.dump(report, ensure_ascii=False, fp=f_out, indent=4)
        f_out.write('{}]') #Hack to close of the json file in the correct format

def batch_loader(args):
    '''
    Creates batches to review, the size of each batch can be change in config.py.
    Opens the metadata file for the samromur corpus and that is provided in config.py. 
    '''
    
    ids = get_ids(args.ids)
    df = pd.read_csv(join(conf['metadata']), sep='\t', dtype='str')
    df = df[df['id'].isin(ids)]
    df.set_index('id', inplace=True)
    data = []
    
    for i in df.index:
        sentence = df.at[i, 'sentence_norm']
        data.append({"tokenId": i, 
                    "recPath": join(conf['recs'], df.at[i, 'filename']),
                    "recId": i,
                    "token": sentence,
                    "valid": df.at[i, 'is_valid']})
    
    
    #Hack for parallelzation
    data = [data[x:x+args.batch_size] for x in range(0, len(data), args.batch_size)]

    log.info(f"\nThere are {len(ids)} in the provided id's file")
    
    if not exists(conf['reports_path']):
        mkdir(conf['reports_path'])
    parallel_processor(create_and_decode, data, args.name, n_jobs=args.n_jobs)

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
        
            f_out.write('{}]') #Hack to close of the json file in the correct format


def create_and_decode_test(data:list):
    ''' 
    make this work the write
    '''
    u_prefix = shortuuid.uuid()

    #Graphs á að vera listi strengur með <tokenID>\t<token>
    graphs = [f"{data['recId']}\t{data['token']}"]
    genGraphs(graphs, u_prefix)
    
    try:
        marosijo = MarosijoTask(modelPath=conf['model'], u_prefix=u_prefix)
        report = marosijo.processBatch([data])
    except expression as e:
        print(e)
        report = []
    
    remove(join('modules', 'local', 'temp', f'{u_prefix}_graphs.scp'))
    remove(join('modules', 'local', 'temp', f'{u_prefix}_graphs.ark'))
    
    return report


def get_ids(path: str) -> list:
    '''
    Load a file with the ids to go over.
    The have to be present in the metadata file
    which is in provided through config.py
    '''
    items =set()
    with open(path) as f_in:
        for line in f_in:
            items.add(str(line.rstrip()))
    return items

def create_and_decode(data:list):
    ''' 
    make this work the write
    '''
    u_prefix = shortuuid.uuid()

    graphs = [f"{r['recId']}\t{r['token']}" for r in data]
    genGraphs(graphs, u_prefix)
    
    try:
        marosijo = MarosijoTask(modelPath=conf['model'], u_prefix=u_prefix)
        report = marosijo.processBatch(data)
    except Exception as e:
        print('Caught error in process batch')
        for line in data:
            print(line)
        print(e)
        report = []
    remove(join('modules', 'local', 'temp', f'{u_prefix}_graphs.scp'))
    remove(join('modules', 'local', 'temp', f'{u_prefix}_graphs.ark'))
    
    return report