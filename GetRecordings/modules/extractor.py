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
        self.threads = args.threads
        self.overwrite = args.overwrite
        self.ids_to_get = args.ids
        
        self.s3 = S3()
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

        # If the output folder exists and we wish to overwrite it, hit enter to proceed.
        # Use with EXTREME CAUTION.
        if exists(self.output_dir) and self.overwrite:
            # Comment this line before using sbatch.
            input('The folder output will be overwritten, click to proceed')
            
            rmtree(self.output_dir)
            os.mkdir(self.output_dir)
            os.mkdir(join(self.output_dir, 'audio'))
            os.mkdir(join(self.output_dir, 'audio_correct_names'))

        # If the output folder exists, just carry on and do nothing.
        elif exists(self.output_dir):
            return

        # If the output folder does not exist, make a new empty one.
        else:
            os.mkdir(self.output_dir)
            os.mkdir(join(self.output_dir, 'audio'))
            os.mkdir(join(self.output_dir, 'audio_correct_names'))

    def get_metadata(self):
        metadata = self.sql.get_all_data_about_clips()
        
        metadata['filename'] = 'NAN'
        metadata.fillna('NAN', inplace=True)
        
        # The data frame returns a few more columns than desired.
        # This filters the columns that we really need.
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

        # Perform multiple mappings on the metadata dataframe
        print('Parsing metadata')
        for i in tqdm(df.index):
            df.at[i, 'id']              = str(df.at[i, 'id']).zfill(7)                          # Pad the id with 0's.
            df.at[i, 'sentence']        = df.at[i, 'sentence'].rstrip()

            df.at[i, 'dialect']         = dialect_mapping(df.at[i, 'dialect'])
            df.at[i, 'age']             = age_mapping(df.at[i, 'age'])
            df.at[i, 'sex']             = gender_mapping(df.at[i, 'sex'])
            df.at[i, 'native_language'] = nationality_mapping(df.at[i, 'native_language'])

        # Use the id column as an index
        # Inplace so that this will be done for THIS dataframe rather than
        # copying it to a new variable (where the 'id' would be used as an index).
        df.set_index('id', inplace =True)

        # Rename the column 'sex' as 'gender'
        df.rename({'sex': 'gender'}, axis='columns', inplace=True)  

        # We use age, gender, language and client_id to give speakers a speaker_id 
        # df['speaker_id'] = create_speaker_ids(df)

        #Create the filenames
        for i in df.index:
            df.at[i, 'filename'] = df.at[i, 'speaker_id'] + '-' + i + '.wav'

        #We no longer need the client_id
        df.drop('client_id', axis=1, inplace=True)
        return df

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

        self.to_file(join(self.output_dir, self.metadata_filename[:-4] + '_inspect.tsv'), df)

    def to_file(self, name, df):
        df.to_csv(name, header=True, sep='\t')

    def parallel_processor(self, function, iterator, n_jobs, chunks=1, units ='files'):
        '''
        This function takes download_clips_parallel() as an argument along with the data (iterator) it is supposed to iterate through.
        '''

        results: list = []
        with ThreadPoolExecutor(max_workers=n_jobs) as executor:
            results = tqdm(executor.map(
                function,
                iterator,
                chunksize=chunks), 
                total=len(iterator),
                unit=' '+ units)
 
    def download_clips(self):
        '''
        Call this function if you intend to download the clips. It prepares the download process before using 
        parallel_processor() to download the clips using download_clips_parallel().
        '''

        print('Downloading clips')
        data = self.sql.get_clips_s3_path()

        # Just a precaution until every row in the database has a speaker_id != null.
        # Hopefully this won't be a issue anymore once the 708 speaker_id-less rows in the database have been
        # taken care of.
        for row in data:
            if not row['speaker_id']:
                raise Exception(f'Row with id: {row['id']} does not contain a speaker_id. Aborting....')

        for row in data:
            # Ready the entire folder structure before commencing download.
            if not exists(join(self.output_dir, 'audio_correct_names', row['speaker_id'])):
                os.mkdir(join(self.output_dir, 'audio_correct_names', row['speaker_id']))

        # parallel_processor() takes care of the rest along with download_clips_parallel().
        self.parallel_processor(self.download_clips_parallel, data, self.threads, chunks=250, units ='files')

        # TODO: Delete output/audio folder when it has become empty. I think this would be the appropriate place to do it, assuming
        #       that all uuid.wav audio clips have been downsampled and deleted at this point.

    def download_clips_parallel(self, row):
        '''
        This function is used by parallel_processor() to iterate through the data. Each call to this function, by parallel_processor(),
        passes a single row of the data - which is fetched in download_clips() - to this function.
        '''
        
        # Download the audio clip from S3. It is initially very large and needs downsampling which is done in fix_header().
        # It also has a temporary filename (uuid) which is fixed during the downsampling process.
        uuid_filename = self.s3.get_object(join(self.output_dir, 'audio'), row['path'])

        # The new filename, after downsampling, will be on the form speaker_id-id.wav
        # Example: 012522-15233.wav
        new_filename = row['speaker_id'] + '-' + row['id'].zfill(7) + '.wav'
        
        # Downsample the temporary file and copy the result to a new folder where all of the audio files are organised.
        self.fix_header(uuid_filename, row['speaker_id'], new_filename)

        # Delete the temporary audio file.
        os.remove(join(self.output_dir, 'audio', uuid_filename))

    def fix_header(self, old_filename, sub_folder, new_filename):
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

        res = sp.run(f'ffmpeg -hide_banner -loglevel warning -i "{self.output_dir}/audio/{old_filename}" -ar 16000 "{self.output_dir}/audio_correct_names/{sub_folder}/{new_filename}"',\
                shell=True,
                stdout=sp.PIPE,
                stderr=sp.PIPE)