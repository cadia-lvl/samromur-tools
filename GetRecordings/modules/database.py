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
        return filepath, filename

class MySQL:

    def __init__(self):
        self.credentials = get_credentials('db')
        self.db = mysql.connect(**self.credentials)
        self.cursor = self.db.cursor(dictionary=True)

    def get_clips(self):
        ids = self.get_ids()
        
        """
        query = ('''
            SELECT 
                *
            FROM 
                clips
           ''')
        """
        
        query = (f'SELECT * FROM clips WHERE id IN {*ids,}')
        self.cursor.execute(query)
        data = self.cursor.fetchall()
        
        return pd.DataFrame(data) 

    def get_ids(self):
        return_list = []
        with open('recs_to_download.txt') as f_in:
            for i in f_in:
                return_list.append(i)
        return return_list
