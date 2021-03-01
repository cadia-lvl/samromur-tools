from os.path import join, exists
from os import mkdir
from shutil import rmtree

import argparse
from pandas import read_csv
import numpy as np

def modify_subset(master_file, subset_file):
    output_path = 'output_m2'
    if not exists(output_path):
        mkdir(output_path)
    else:
        print('Overwriting previous output...')
        rmtree(output_path)
        mkdir(output_path)

    # Read both files to a data frame.
    master_df = read_csv(master_file, sep='\t', dtype=str)
    subset_df = read_csv(subset_file, sep='\t', dtype=str)

    subset_ids_padded = list(map(lambda i: i.zfill(7), list(subset_df['id'])))              # For each id in subset_df, put to a separate list where each id is zero padded.
    master_df = master_df[master_df['id'].isin(subset_ids_padded)]                           # Create a new subset of the master file, based on the id's that are present in the old subset file.

    master_df['status'] = 'NAN'             # Add a new empty column.
    master_df.fillna('NAN', inplace=True)   # Each empty cell is filled with NAN.

    # Use both df's id column as an index.
    subset_df.set_index('id', inplace =True)
    master_df.set_index('id', inplace =True)

    # For each row in master_df, where its id value matches an id value in a row in subset_df, copy status and released value from subset_df to that matching row in master_df.
    counter = 0
    for id in subset_ids_padded:
        master_df.at[id, 'status'] = subset_df.at[id.lstrip('0'), 'status']
        master_df.at[id, 'released'] = subset_df.at[id.lstrip('0'), 'released']

    # Rename 'released', which implies a boolean value, to 'release' which implies a release number
    master_df.rename({'released': 'release'}, axis='columns', inplace=True)  

    master_df.to_csv(join(output_path, 'r1_metadata.tsv'), header=True, sep='\t')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Reads a master metadata file, takes a subset of it based on ids present in another subset metadata file, makes modifications on the new subset and writes it to a new file.',
        add_help=True,
        formatter_class=argparse.MetavarTypeHelpFormatter)
    
    parser.add_argument(
        '-m', '--master', required=False, default='../../../samromur-data/as_of_050221/050221_metadata/metadata_all_clips_inspect_scored_normalized.tsv', type=str, help='Path to master metadata file')

    parser.add_argument(
        '-s', '--subset', required=False, default='../../../samromur-data/metadata_general_r1.tsv', type=str, help='Path to subset metadata file')

    args = parser.parse_args()

    modify_subset(args.master, args.subset)
    print('Finished')