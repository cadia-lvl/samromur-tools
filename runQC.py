from modules.MarosijoModule import MarosijoTask
from modules.MarosijoGenGraphs import genGraphs
from modules.procces_batch import batch_loader
from db.extractor import Extractor

from os.path import join, exists
from os import mkdir
from json import dump
from config import conf
from argparse import ArgumentParser
    

def download_and_run_QC(name, ids_to_clips):
    recordings = Extractor(ids_to_clips).run()     
    genGraphs(join(conf['archive'], 'tokens.txt'))   
    marri = MarosijoTask(modelPath= conf['model'], downsample=True)
    report = marri.processBatch(recordings)

    if not exists(conf['reports_path']):
        mkdir(conf['reports_path'])

    with open(join(conf['reports_path'], f"{name}.json"), 'w') as fout:
        dump(report, ensure_ascii=False, fp=fout, indent=4)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--name', type=str, default='report', help='Arbritary session name')    
    parser.add_argument('--download', type=str, default=None, help='Path to file with ids to download and examine')
    parser.add_argument('--ids', type=str, default=None, help='Path to file with ids in a given metadata file to examine')
    args = parser.parse_args()
    
    if args.download:
        download_and_run_QC(args.name, args.download)
    else:
        batch_loader(args.name, conf, args.ids )

  
