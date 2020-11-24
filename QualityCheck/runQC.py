from argparse import ArgumentParser
import json
from os.path import join

from modules.procces_batch import batch_loader
from config import conf

def parse_reports(args):
    path=join(conf['reports_path'], f"{args.name}.json")
    print(path)
    with open (path) as f_in:
        report = json.load(f_in)

    with open(join(conf['reports_path'],f"{args.name}_summary.txt"), 'w') as f_out:
        for line in report:
            if line:
                f_out.write(f"{line['recordingId']}\t{line['stats']['accuracy']}\n")

if __name__ == '__main__':
    import time
    start = time.time()  

    parser = ArgumentParser()
    parser.add_argument('--name', type=str, default='report', help='Arbritary session name')    
    parser.add_argument('--ids', type=str, default='ids_to_check', help='Path to file with ids in a given metadata file to examine')
    args = parser.parse_args()
    
    batch_loader(args)

    parse_reports(args)
    end = time.time()
    print(f"Run time {(end - start)/60} min")
