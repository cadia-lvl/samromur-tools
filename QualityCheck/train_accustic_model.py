from os.path import join
from training.utils import prep_data, train_acoustic
from config import conf

def read_ids_from_file(path):
    ids = []
    with open(path) as f_in:
        for line in f_in:
            ids.append((line.strip()).zfill(7))

    return ids

if __name__ == '__main__':
    prep_data(conf, read_ids_from_file(join('training', 'ids', '230321')))
    train_acoustic(conf)