from os.path import join, exists, getsize
import pandas as pd
import numpy as np
import os
from shutil import rmtree
from datetime import date
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import subprocess as sp
import re


from modules.database import S3, MySQL
from modules.audio_tools import read_audio, get_duration, save_audio, detect_empty_waves
from modules.mapping import age_mapping, gender_mapping, nationality_mapping, dialect_mapping
from modules.create_speaker_ids import create_speaker_ids

class Extractor:
    def __init__(self, args):
        self.output_dir = args.output
        self.metadata_filename = args.metadata
        self.recs_file = 'db_rec_names.tsv'
        self.threads=args.threads
        self.overwrite = args.overwrite
        self.s3 = S3()
        self.ids_to_get = args.ids
        self.sql = MySQL(self.open_ids_file())

        self.ensure_dirs()
        self.filenames_skitamix = {}

    def skitamix(self):
        temp:dict = {}
        df = pd.read_csv(join(self.output_dir, self.metadata_filename), index_col='id', sep='\t')
        for i in df.index:
            temp_i = str(i).zfill(7)
            temp[temp_i] = df.at[i, 'filename']
        self.filenames_skitamix = temp


    def open_ids_file(self):
            return_list = []
            with open(self.ids_to_get) as f_in:
                for i in f_in:
                    return_list.append(i)
            return return_list

    def ensure_dirs(self):
        '''
        Create folders if necessary
        '''
        if exists(self.output_dir): #This might cuase trouble when downloading
            input('The folder output will be overwritten, click to proceed')
            rmtree(self.output_dir)
            os.mkdir(self.output_dir)
            os.mkdir(join(self.output_dir, 'audio'))
            os.mkdir(join(self.output_dir, 'audio_correct_names'))
        else:
            os.mkdir(self.output_dir)
            os.mkdir(join(self.output_dir, 'audio'))
            os.mkdir(join(self.output_dir, 'audio_correct_names'))


    def get_metadata(self):
        metadata = self.sql.get_all_data_about_clips()
        # metadata['speaker_id'] = 'NAN'
        metadata['filename'] = 'NAN'
        metadata.fillna('NAN', inplace=True)
        
        # The data frame returns a few more columns than desired.
        # This filters the columns that we really need here.
        metadata = metadata[['id',
 #                           'speaker_id', 
 #                           'filename',
                            'client_id',
                            'sentence',
                            'sex',
                            'age',
                            'native_language',
                            'dialect',
                            'created_at',
                            'is_valid',
                            'empty',
                            'duration',
                            'sample_rate',
                            'size',
                            'user_agent']]

        metadata = self.parse_metadata(metadata)
        name = join(self.output_dir, self.metadata_filename)
        self.to_file(name, metadata)

        self.skitamix()

    def parse_metadata(self, df):
        '''
        Helper function for get_metadata
        '''
        # Needed to zero pad the ids
        df = df.astype(str)

        # Preform multible mappings on the metadata dataframe
        print('Parsing metadata')
        for i in tqdm(df.index):
            df.at[i, 'id'] = str(df.at[i, 'id']).zfill(7)
            df.at[i, 'sentence'] = df.at[i, 'sentence'].rstrip()
            df.at[i, 'dialect'] = dialect_mapping(df.at[i, 'dialect'])
            df.at[i, 'age'] = age_mapping(df.at[i, 'age'])
            df.at[i, 'sex'] = gender_mapping(df.at[i, 'sex'])
            df.at[i, 'native_language'] = nationality_mapping(df.at[i, 'native_language'])

        # Use the id column as an index
        # Inplace so that this will be done for THIS dataframe rather than
        # copying it to a new variable (where the 'id' would be used as an index).
        df.set_index('id', inplace =True)

        # Rename the coloumn sex as gender
        df.rename({'sex': 'gender'}, axis='columns', inplace=True)  

        #we use age, gender, langugae and client id to give speakers a speaker id 
        df['speaker_id'] = create_speaker_ids(df)

        #Create the filenames
        for i in df.index:
            df.at[i, 'filename'] = df.at[i, 'speaker_id'] + '-' + i + '.wav'

        #We no longer need the client_id
        df.drop('client_id', axis=1, inplace=True)
        return df

    def inspect_audio_only_those_with_NAN(self):
        '''
        Finds clips that don't have duration or file size and add that to the metadata file.

        We also use a package to examine if clips are empty.
        '''

        df = pd.read_csv(join(self.output_dir, self.metadata_filename), sep='\t', dtype=str)
        df.set_index('id', inplace=True)

        recs:dict = {}
        with open(join(self.output_dir, self.recs_file)) as f_in:
            for line in f_in:
                id, filename = line.split('\t')
                id = id.zfill(6)
                recs[id] = filename.rstrip()
        
        print('Inspecting audio')
        for i in tqdm(df.index):
            # We will be downsampling in the next step
            df.at[i, 'sample_rate'] = 16000

            if df.at[i, 'duration'] == 'NAN':
                try:
                    wave, sr = read_audio(join(self.output_dir, 'audio', recs[i]))
                    df.at[i, 'duration']  = get_duration(wave, sr)
                except Exception  as e:
                    print(f"Error working with file {i}\n\n{e}")
                
            if df.at[i, 'size'] == 'NAN':
                try:
                    df.at[i, 'size'] = getsize(join(self.output_dir, 'audio', recs[i]))
                except Exception  as e:
                    print(f"Error working with file {i}\n\n{e}")

            if df.at[i, 'empty'] == 'NAN':
                try:
                    df.at[i, 'empty'] = detect_empty_waves(join(self.output_dir, 'audio', recs[i]))
                except Exception  as e:
                    print(f"Error working with file {i}\n\n{e}")

        name = join(self.output_dir, self.metadata_filename[:-4] + '_inspect.tsv')
        self.to_file(name, df)

    def inspect_all_audio_files(self):
        '''
        Finds clips that don't have duration or file size and add that to the metadata file.
        We also use a package to examine if clips are empty.
        '''
        
        df = pd.read_csv(join(self.output_dir, self.metadata_filename), sep='\t', dtype=str)
        df.set_index('id', inplace=True)

        print('Inspecting audio')
        for i in tqdm(df.index):
            # Legend      :   output root    /  corrected names     / speaker id                          / filename (speaker_id-recording_id)
            # Default path:   output         /  audio_correct_names / 00000x                              / 00000x-000000x.wav
            audio_clip = join(self.output_dir, 'audio_correct_names', str(df.at[i, 'speaker_id']).zfill(6), df.at[i, 'filename'])
            try:
                wave, sr = read_audio(audio_clip)
                df.at[i, 'duration']  = get_duration(wave, sr)
                df.at[i, 'sample_rate'] = sr
            except Exception as e:
                print(f"Error working with file {i}\n\n{e}")
                
            try:
                df.at[i, 'size'] = getsize(audio_clip)
            except Exception as e:
                print(f"Error working with file {i}\n\n{e}")

            try:
                df.at[i, 'empty'] = int(detect_empty_waves(audio_clip))
            except Exception as e:
                print(f"Error working with file {i}\n\n{e}")

        name = join(self.output_dir, self.metadata_filename[:-4] + '_inspect.tsv')
        self.to_file(name, df)

    def to_file(self, name, df):
        df.to_csv(name, header=True, sep='\t')

    def parallel_processor(self, function, iterator, n_jobs, chunks=1, units ='files'):
        results: list = []
        with ThreadPoolExecutor(max_workers=n_jobs) as executor:
            results =  tqdm(executor.map(
                function,
                iterator,
                chunksize=chunks), 
                total=len(iterator),
                unit= ' '+ units)
 
    def download_clips_parallel(self):
        print('Downloading clips')
        data = self.sql.get_clips_s3_path()

        for i in data:
            id = str(i['id']).zfill(7)
            new_filename = self.filenames_skitamix[id]
            speaker_id = re.sub('-.+','', new_filename) 

            if not exists(join(self.output_dir, 'audio_correct_names', speaker_id)):
                os.mkdir(join(self.output_dir, 'audio_correct_names', speaker_id))

        self.parallel_processor(self.download_clips_p, data, self.threads, chunks=250, units ='files')

    def download_clips_p(self, data):
        '''
        Add description
        '''
        
        uuid_filename = self.s3.get_object(join(self.output_dir, 'audio'), data['path'])
        #new_filname = data['speaker_id'] + '-' + data['id'].zfill(7) + '.wav'

        id = str(data['id']).zfill(7)
        new_filename = self.filenames_skitamix[id]
        speaker_id = re.sub('-.+','', new_filename) 
        
        
        #self.fix_header(uuid_filename, data['speaker_id'], new_filename)
        self.fix_header(uuid_filename, speaker_id, new_filename)

        os.remove(join(self.output_dir, 'audio', uuid_filename))


    def fix_header(self, old_filename, sub_folder, new_filname):
        """
        Fix headers in the wav files and downsample to 16khz.
        We also add the clips in a folder structure that is.
        
        output/
            audio_correct_names/
                speaker_id 1/
                    audio_clip 1
                        ...
                    audio_clip n
                speaker_id 2/
                    ...
                speaker_id n/
        """

        res = sp.run(f'ffmpeg -hide_banner -loglevel warning -i "{self.output_dir}/audio/{old_filename}" -ar 16000 "{self.output_dir}/audio_correct_names/{sub_folder}/{new_filname}"',\
                shell=True,
                stdout=sp.PIPE,
                stderr=sp.PIPE)