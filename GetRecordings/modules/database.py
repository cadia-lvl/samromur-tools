from os.path import join
from uuid import uuid4
import boto3
import mysql.connector as mysql
import pandas as pd

from utils.config import get_credentials
class S3:
    
    def __init__(self):
        self.bucket = 'samromur.is'
        self.credentials = get_credentials('s3')
        self.session = boto3.Session(**self.credentials)
        self.client = self.session.client('s3')

    def get_object(self, output_dir, path):
        filename = str(uuid4()) + '.wav'
        filepath = join(output_dir, filename)
        with open(filepath, 'wb') as _file:
            self.client.download_fileobj(self.bucket, path, _file)
        return filename

class MySQL:

    def __init__(self, ids_to_get):
        self.credentials = get_credentials('db')
        self.db = mysql.connect(**self.credentials)
        self.cursor = self.db.cursor(dictionary=True)
        self.ids = ids_to_get

    def get_all_data_about_clips(self):
        ids = self.ids

        query = (f'SELECT * FROM clips WHERE id IN {*ids,}')
        # query = ('SELECT * FROM clips')
        
        #query = ('SELECT * FROM clips where created_at > "2021-01-01" and created_at < "2021-01-20"')
        #query = ('SELECT * FROM clips where created_at > "2021-01-19"')
        #query = ('SELECT * FROM clips where created_at > "2021-01-01"')
        
        self.cursor.execute(query)
        data = self.cursor.fetchall()
        
        return pd.DataFrame(data) 

    def get_clips_s3_path(self):
        '''
        Reads the id's to get from the file recs_to_download.txt. Does a call to the 
        sql server and returns a list of dictionaries where each dict as a "id" and "path" object.
        id is the clip id and the path is the path to the s3 bucket of that clip.
        '''
        ids = self.ids
        
        query = (f'SELECT id, speaker_id, path FROM clips WHERE id IN {*ids,}')
        # query = ('SELECT id, speaker_id, path FROM clips limit 10')
        
        #query = ('SELECT id, path FROM clips where created_at > "2021-01-01" and created_at < "2021-01-20"')
        #query = ('SELECT * FROM clips where created_at > "2021-01-19"')
        #query = ('SELECT * FROM clips where created_at > "2021-01-01"')

        self.cursor.execute(query)        
        return self.cursor.fetchall()
        
