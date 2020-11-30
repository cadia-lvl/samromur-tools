from os.path import join, exists
from uuid import uuid4
import pandas as pd
import numpy as np
import enlighten
import os
from shutil import rmtree

from modules.database import S3, MySQL
from inspect_data.audio_tools import read_audio, get_duration, save_audio
from modules.mapping import speaker_mapping, age_mapping, gender_mapping, nationality_mapping, dialect_mapping



class Extractor:
    def __init__(self):
        self.output_dir = './output'
        self.ensure_dirs(self.output_dir)
        self.s3 = S3()
        self.sql = MySQL()
        self.clips = self.sql.get_clips()

    def ensure_dirs(self, root_dir):
        '''
        Create folders if necessary
        '''
        if exists(root_dir):
            input('The folder output will be overwritten, click to proceed')
            rmtree(root_dir)
        os.mkdir(root_dir)
        os.mkdir(join(root_dir, 'audio'))

    def parse_dataframe(self, folder, df):
        placeholder = np.zeros(len(df))
        new_df = pd.DataFrame(
            np.column_stack([
                df['id'],
                df['path'],
                placeholder,
                df['client_id'],
                df['sentence'],
                placeholder,
                df['sex'],
                df['age'],
                df['native_language'],
                df['created_at'],
                df['user_agent'],
                df['is_valid'],
                placeholder,
                placeholder,
                df['institution'],
                df['needs_votes'],
                df['division'],
                df['dialect'],
                placeholder

            ]), 
            columns=[
                'id',
                'path',
                'uuid',
                'client_id',
                'sentence',
                'duration',
                'sex',
                'age',
                'native_language',
                'created_at',
                'user_agent',
                'is_valid',
                'samplExtractore_rate',
                'speaker_id',
                'institution',
                'needs_votes',
                'division',
                'dialect',
                'sample_rate'
            ]
        )
        return new_df

    def run(self):
        metadata_df = self.parse_dataframe('audio', self.clips)
    
        pbar = enlighten.Counter(total=len(metadata_df), desc='Downloading and parsing data')
        
        metadata_df = self.add_data('audio', metadata_df, pbar)
        
        #metadata_df = metadata_df[['id','created_at', 'sex', 'age','dialect','duration', 'sample_rate', 'sentence', 'uuid']]

        metadata_df = metadata_df[['id','path', 'uuid','created_at', 'client_id', 'division',
        'speaker_id', 'is_valid', 'sex', 'age', 'native_language', 'dialect',
         'duration', 'sample_rate', 'sentence', 'user_agent']]
                
        self.to_file('metadata', metadata_df)

    def to_file(self, name, df):
        df.to_csv(join(self.output_dir, name+'.tsv'), header=True, index=False, sep='\t')


    def add_data(self, folder, df, pbar):
        '''
        Adds data that isn't directly taken out of the database
        '''
        speakers_mapping:dict = speaker_mapping(df)
        
        for _, row in df.iterrows():
            filepath, filename = self.s3.get_object(join(self.output_dir, folder), row['path'])
            wave, sr = read_audio(filepath)
            row['sentence'] = row['sentence'].rstrip()
            row['uuid'] = filename.rstrip()
            row['duration'] = get_duration(wave, sr)
            row['sample_rate'] = sr
            row['dialect'] = dialect_mapping(row['dialect'])
            row['speaker_id'] = speakers_mapping[row['client_id']]
            row['age'] = age_mapping(row['age'])
            row['sex'] = gender_mapping(row['sex'])
            row['native_language'] = nationality_mapping(row['native_language'])
            pbar.update()
        return df