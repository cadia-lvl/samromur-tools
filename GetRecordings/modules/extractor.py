from os.path import join, exists, getsize
import pandas as pd
import os
from shutil import rmtree
from datetime import date
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import subprocess as sp
import math
from datetime import date

from modules.database import S3, MySQL
from modules.audio_tools import read_audio, get_duration, detect_empty_waves
from modules.mapping import age_mapping, gender_mapping, nationality_mapping, dialect_mapping

class Extractor:
    def __init__(self, args):
        self.output_dir = args.output
        self.metadata_filename = args.metadata
        self.threads = args.threads
        self.overwrite = args.overwrite
        self.ids_to_get = args.ids
        self.download_only_missing = args.download_only_missing

        # MEC mode variables.
        self.mec = args.metadata_existing_clips
        self.mec_filename = 'metadata_all_clips.tsv'      if self.mec else None
        self.mec_path = args.metadata_existing_clips_path if self.mec else None

        self.update_path = args.update
        
        self.s3 = S3()

        # If in MEC mode, get all ids from already downloaded audio files.
        # Otherwise, read ids to get from text file.
        self.sql = MySQL(self.open_ids_file() if not self.mec else self.mec_get_ids())

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
            # If audio folder does not exist, make a new empty one
            if (~exists(join(self.output_dir, 'audio'))):
                os.mkdir(join(self.output_dir, 'audio'))
            if ~exists(join(self.output_dir, "audio_correct_names")):
                os.mkdir(join(self.output_dir, 'audio_correct_names'))
            return

        # If the output folder does not exist, make a new empty one.
        else:
            os.mkdir(self.output_dir)
            os.mkdir(join(self.output_dir, 'audio'))
            os.mkdir(join(self.output_dir, 'audio_correct_names'))

    def mec_get_ids(self):
        '''MEC mode: Gets ids of clips that have already been downloaded and returns a list of them.'''

        lis:list = []

        for root, dirs, audio_files in os.walk(self.mec_path):
            for audio_file in audio_files:
                # For each file, isolate its id and append to list.

                # How we isolate each file's id:
                # 
                # '006006-0047496.wav' -> ['006006', '0047496.wav'] -> ['0047496', 'wav'] -> '0047496' -> 47496 -> '47496'

                lis.append(int(audio_file.split('-')[1].split('.')[0]))

        lis.sort()  # No need to sort perhaps?

        # Change each id to string appended with a newline before returning.
        return list(map(lambda x: str(x) + '\n', lis))

    def update_metadata(self):
        """Update mode: Using an existing metadata file, creates a new updated one with the newest clip validity information from the database."""

        metadata = pd.read_csv(self.update_path, sep='\t', dtype=str)
        metadata.set_index('id', inplace=True)

        # Get df which contains all entries from db with id and is_valid columns
        is_valid_new = self.sql.get_is_valid()

        # Filter them so we only get the same ones as we have in our metadata
        local_ids:list = list(map(lambda x: int(x), list(metadata.index)))
        is_valid_new = is_valid_new[is_valid_new['id'].isin(local_ids)]
        is_valid_new.set_index('id', inplace=True)

        print(f'Metadata entries: {len(metadata)}')
        print(f'Database entries: {len(is_valid_new)}')

        with open('update_log.txt', 'a') as f_out:
            update_count:int = 0
            for id in tqdm(metadata.index):
                prev_value = metadata.at[id, 'is_valid']
                new_value = str(is_valid_new.at[int(id), 'is_valid'])

                # If the is_valid value of fetched data is 'nan', we capitalize it to 'NAN' so that it matches the value we use in the local metadata.
                if math.isnan(float(new_value)):
                    new_value = 'NAN'

                if prev_value != new_value:
                    metadata.at[id, 'is_valid'] = new_value
                    update_count += 1

                    f_out.write(f'{id}\tOLD: {prev_value} - NEW: {new_value}\n')

        file_name = f'{self.update_path.split("/")[-1][:-4]}_updated.tsv'

        print(f'{update_count} records have been verified since last update')
        print(f'Writing updated metadata to {file_name}...')
        self.to_file(file_name, metadata)
        return False

    def get_metadata(self):
        if self.update_path != '':
            print('Updating metadata file...')
            return self.update_metadata()

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

        # Just a precaution until every row in the database has a speaker_id != null.
        # Hopefully this won't be a issue anymore once the 700+ speaker_id-less rows in the database have been
        # taken care of.
        try:
            for i in metadata.index:
                if metadata.at[i, 'speaker_id'] == 'NAN':
                    raise Exception()
        except Exception as e:
            print(f'Row with id: {metadata.at[i, "id"]} does not contain a speaker_id. Aborting....')
            return False

        metadata = self.parse_metadata(metadata)

        name = join(self.output_dir, (self.metadata_filename if not self.mec else self.mec_filename))
        self.to_file(name, metadata)

        return True

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
        
        df = pd.read_csv(join(self.output_dir, (self.metadata_filename if not self.mec else self.mec_filename)), sep='\t', dtype=str)
        df.set_index('id', inplace=True)

        print('Inspecting audio')
        for i in tqdm(df.index):

            # Legend      :   output root    /  corrected names     / speaker id                          / filename (speaker_id-recording_id)
            # Default path:   output         /  audio_correct_names / 00000x                              / 00000x-000000x.wav
            audio_clip = join(self.output_dir, 'audio_correct_names', str(df.at[i, 'speaker_id']).zfill(6), df.at[i, 'filename']) if not self.mec \
                    else join(self.mec_path, str(df.at[i, 'speaker_id']).zfill(6), df.at[i, 'filename'])
            
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

        self.to_file(join(self.output_dir, (self.metadata_filename if not self.mec else self.mec_filename)[:-4] + '_inspect.tsv'), df)

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

        # MEC (metadata for existing clips) mode skips the download step.
        if self.mec:
            print('MEC mode on - skipping download procedure...')
            return

        input('Download will commence now\nHit "Enter" to continue...')     # Put this here for precaution.

        print('Downloading clips')
        data = self.sql.get_clips_s3_path()

        for row in data:
            # Ready the entire folder structure before commencing download.
            if not exists(join(self.output_dir, 'audio_correct_names', row['speaker_id'])):
                os.mkdir(join(self.output_dir, 'audio_correct_names', row['speaker_id']))

            # self.download_clips_parallel(row)     # Use this line for easier debug experience, by not using threads. Just remember to comment out the call to parallel_processor() below!

        if self.download_only_missing:
            with open('skipped.txt', 'w') as skipped:
                skipped.write(f'Already existing ids as of {date.today()}:\n')

        # parallel_processor() takes care of the rest along with download_clips_parallel().
        self.parallel_processor(self.download_clips_parallel, data, self.threads, chunks=250, units ='files')

        # TODO: Delete output/audio folder when it has become empty. I think this would be the appropriate place to do it, assuming
        #       that all uuid.wav audio clips have been downsampled and deleted at this point.

    def download_clips_parallel(self, row):
        '''
        This function is used by parallel_processor() to iterate through the data. Each call to this function, by parallel_processor(),
        passes a single row of the data - which is fetched in download_clips() - to this function.
        '''
        
        # The new filename, after downsampling, will be on the form speaker_id-id.wav
        # Example: 012522-15233.wav
        new_filename = row['speaker_id'] + '-' + str(row['id']).zfill(7) + '.wav'

        # Only download missing files if set in arguments
        if self.download_only_missing:
            new_file_path = join(self.output_dir,"audio_correct_names",row["speaker_id"],new_filename)
            if exists(new_file_path):
                try:
                    with open('skipped.txt', 'a') as skipped:
                        skipped.write(f'{row["id"]}\n')
                except IOError as e:
                    print(e)
                return

        # Download the audio clip from S3. It is initially very large and needs downsampling which is done in fix_header().
        # It also has a temporary filename (uuid) which is fixed during the downsampling process.
        uuid_filename = self.s3.get_object(join(self.output_dir, 'audio'), row['path'])


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