from os.path import join, exists
from os import mkdir
from shutil import copyfile

import argparse
from pandas import read_csv
from tqdm import tqdm
import numpy as np

def create_speaker_folders(metadata_df, p_train, p_test, p_dev):
    print('Creating folders...')
    for id in tqdm(metadata_df.index):
        if metadata_df.at[id, 'status'] == 'train':
            dir = join(p_train, metadata_df.at[id, 'speaker_id'])
            if not exists(dir):
                mkdir(dir)

        elif metadata_df.at[id, 'status'] == 'test':
            dir = join(p_test, metadata_df.at[id, 'speaker_id'])
            if not exists(dir):
                mkdir(dir)

        elif metadata_df.at[id, 'status'] == 'dev':
            dir = join(p_dev, metadata_df.at[id, 'speaker_id'])
            if not exists(dir):
                mkdir(dir)

def create_and_populate_r1_folder(metadata_path, audio_path, output_path):
    if not exists(output_path):
        mkdir(output_path)
    else:
        print('Output path already exists.\nPlease manually delete the output folder and rerun this script if you wish to overwrite.')
        return
    
    copyfile(metadata_path, join(output_path, 'metadata.tsv'))

    r1_path    = 'r1'
    train_path = join(output_path, r1_path, 'train')
    test_path  = join(output_path, r1_path, 'test')
    dev_path   = join(output_path, r1_path, 'dev')

    mkdir(join(output_path, r1_path))
    mkdir(train_path)
    mkdir(test_path)
    mkdir(dev_path)

    metadata_df = read_csv(metadata_path, sep='\t', dtype=str)
    metadata_df.set_index('id', inplace=True)

    create_speaker_folders(metadata_df, train_path, test_path, dev_path)

    print('Copying files...')
    for id in tqdm(metadata_df.index):
        filename = f"{metadata_df.at[id, 'filename'][:-4]}.flac"
        path_to_file = join(audio_path, metadata_df.at[id, 'speaker_id'], filename)

        if metadata_df.at[id, 'status'] == 'train':
            copyfile(path_to_file, join(train_path, metadata_df.at[id, 'speaker_id'], filename))
            continue
        elif metadata_df.at[id, 'status'] == 'test':
            copyfile(path_to_file, join(test_path, metadata_df.at[id, 'speaker_id'], filename))
            continue
        elif metadata_df.at[id, 'status'] == 'dev':
            copyfile(path_to_file, join(dev_path, metadata_df.at[id, 'speaker_id'], filename))
    
    print('Finished')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Creates a folder structure and copies audio files to correct folders using information in a metadata file as a guide. Copies the metadata file itself to the root of the output path as well.',
        add_help=True,
        formatter_class=argparse.MetavarTypeHelpFormatter)
    
    parser.add_argument(
        '-m', '--metadata', required=False, default='metadata_output/r1_metadata.tsv', type=str, help='Path to the subset metadata file')

    parser.add_argument(
        '-a', '--audio', required=False, default='../../../../../samromur-data/as_of_050221/050221_audio_clips/audio_clips_flac/', type=str, help='Path to the audio files. Flac version.')

    parser.add_argument(
        '-o', '--output', required=False, default='Samromur', type=str, help='Path to subset metadata file')

    args = parser.parse_args()

    create_and_populate_r1_folder(args.metadata, args.audio, args.output)