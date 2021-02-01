from os.path import join, exists, getsize
import pandas as pd
import numpy as np
import os
from shutil import rmtree
from datetime import date
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import subprocess as sp

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
        if exists(self.output_dir) and self.overwrite:
            input('The folder output will be overwritten, click to proceed')
            rmtree(self.output_dir)
            os.mkdir(self.output_dir)
            os.mkdir(join(self.output_dir, 'audio'))
            os.mkdir(join(self.output_dir, 'audio_correct_names'))
   
    def parallel_processor_with_no_return(self, function, iterator, n_jobs, chunks=2500, units ='files'):
        #Chunk size should be 1 in acordance with the hack above
        with ProcessPoolExecutor(max_workers=n_jobs) as executor:
            results =  tqdm(executor.map(
                function,
                iterator,
                chunksize=chunks), 
                total=len(iterator),
                unit= ' '+ units) 
    
    def parallel_processor(self, function, iterator, n_jobs, chunks=1, units ='files'):
        #Chunk size should be 1 in acordance with the hack above
        results: list = []
        with open(join(self.output_dir, self.recs_file), 'w') as f_out:
            with ThreadPoolExecutor(max_workers=n_jobs) as executor:
                results =  tqdm(executor.map(
                    function,
                    iterator,
                    chunksize=chunks), 
                    total=len(iterator),
                    unit= ' '+ units)
                for line in results:
                    f_out.write(f"{line[0]}\t{line[1]}\n")

    def download_clips_parallel(self):
        print('Downloading clips')
        data = self.sql.get_clips_s3_path()
        self.parallel_processor(self.download_clips_p, data, self.threads, chunks=250, units ='files')

    def download_clips_p(self, data):
        '''
        Function that downloads the clips to "output_dir" and creates
        tab separate file with the lines <clip-id>\t<uuid-filename>
        '''
        #data = self.sql.get_clips_s3_path()
        #print('Downloading')
        filename = self.s3.get_object(join(self.output_dir, 'audio'), data['path'])
        return [data['id'], filename]

  
    def download_clips(self, data):
        '''
        Function that downloads the clips to "output_dir" and creates
        tab separate file with the lines <clip-id>\t<uuid-filename>
        '''
        #data = self.sql.get_clips_s3_path()
        #print('Downloading')
        with open(join(self.output_dir, self.recs_file), 'w') as f_out:
            for line in data:
                filename = self.s3.get_object(join(self.output_dir, 'audio'), line['path'])
                f_out.write(f"{line['id']}\t{filename}\n")
    
    def get_metadata(self):
        metadata = self.sql.get_all_data_about_clips()
        metadata['speaker_id'] = 'NAN'
        metadata['filename'] = 'NAN'
        metadata.fillna('NAN', inplace=True)
        metadata = metadata[['id',
                            'speaker_id', 
                            'filename',
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

    def parse_metadata(self, df):
        '''
        Helper function for get_metadata
        '''
        # Needed to zero pad the ids
        df = df.astype(str)

        # Preform multible mappings on the metadata dataframe
        print('Parsing metadata')
        for i in tqdm(df.index):
            df.at[i, 'id'] = str(df.at[i, 'id']).zfill(6)
            df.at[i, 'sentence'] = df.at[i, 'sentence'].rstrip()
            df.at[i, 'dialect'] = dialect_mapping(df.at[i, 'dialect'])
            df.at[i, 'age'] = age_mapping(df.at[i, 'age'])
            df.at[i, 'sex'] = gender_mapping(df.at[i, 'sex'])
            df.at[i, 'native_language'] = nationality_mapping(df.at[i, 'native_language'])

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

        recs:dict = {}
        with open(join(self.output_dir, self.recs_file)) as f_in:
            for line in f_in:
                id, filename = line.split('\t')
                id = id.zfill(6)
                recs[id] = filename.rstrip()
        
        print('Inspecting audio')
        for i in tqdm(df.index):
            try:
                wave, sr = read_audio(join(self.output_dir, 'audio', recs[i]))
                df.at[i, 'duration']  = get_duration(wave, sr)
                df.at[i, 'sample_rate'] = sr
            except Exception as e:
                print(f"Error working with file {i}\n\n{e}")
                
            try:
                df.at[i, 'size'] = getsize(join(self.output_dir, 'audio', recs[i]))
            except Exception as e:
                print(f"Error working with file {i}\n\n{e}")

            try:
                df.at[i, 'empty'] = int(detect_empty_waves(join(self.output_dir, 'audio', recs[i])))
            except Exception as e:
                print(f"Error working with file {i}\n\n{e}")

        name = join(self.output_dir, self.metadata_filename[:-4] + '_inspect.tsv')
        self.to_file(name, df)

    def fix_header(self):
        """
        Fix headers is beacause we have had a bug when recording, that function will
        also downsample the recordings to 16khz.
        """
        df = pd.read_csv(join(self.output_dir, self.metadata_filename), sep='\t', dtype=str)
        df.set_index('id', inplace=True)

        recs:dict = {}
        with open(join(self.output_dir, self.recs_file)) as f_in:
            for line in f_in:
                id, filename = line.split('\t')
                id = id.zfill(6)
                recs[id] = filename.rstrip()
                
        iterator:list = []
        for i in df.index:
            iterator.append([recs[i], df.at[i, 'filename']])

        print('Fixing header and downsampling')
        #def parallel_processor_with_no_return(self, function, iterator, n_jobs, chunks=2500, units ='files'):

        #self.parallel_processor_with_no_return(self.fix_header_func, iterator, n_jobs=5, chunks=10)
        for line in tqdm(iterator):
            self.fix_header_func(line)
            

    def to_file(self, name, df):
        df.to_csv(name, header=True, sep='\t')

    def fix_header_func(self, d:list):
        """
        Fix headers in the wav files and downsample to 16khz.
        """
        res = sp.run(f'ffmpeg -hide_banner -loglevel warning -i "teens/audio/{d[0]}" -ar 16000 "teens/audio_correct_names/{d[1]}"',\
                shell=True,
                stderr=sp.PIPE,
                stdout=sp.PIPE)
            
        if res.stderr:
            print(res.stderr)