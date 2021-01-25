import pandas as pd


"""
metadata = '/home/derik/work/samromur-tools/GetRecordings/output_311220/metadata_2020-12-29.tsv'
df = pd.read_csv(metadata, sep='\t', dtype=str)
df.set_index('id', inplace=True)

for i in df.index:
# is_valid != '1.0'
# empty != True, 1
# released != 'V1'
    if df.at[i, 'is_valid'] != '1' \
        and df.at[i, 'empty'] != '1' \
        and df.at[i, 'released'] != 'V1':

        '''print(
            df.at[i, 'is_valid'],  
            df.at[i, 'empty'] ,
            df.at[i, 'empty'] ,
            df.at[i, 'released'])
        input()'''
        print(i)       
"""


"""
import json
with open('reports/hope_this_workssss.json') as file:
  data = json.load(file)

for line in data:
    print(line['recordingId'])

"""

"""
from tqdm import tqdm
metadata = '/home/derik/work/samromur-tools/GetRecordings/output_311220/metadata_2020-12-29.tsv'
df = pd.read_csv(metadata, sep='\t', dtype=str)
df.set_index('id', inplace=True)

check = set()
with open('log/faileed copy') as f_in:
    for line in f_in:
        line = line.rstrip()
        check.add(line)

check = set()
with open('done') as f_in:
    for line in f_in:
        line = line.rstrip()
        check.add(line)

for i in df.index:
    if 'c' in df.at[i, 'sentence_norm'] or 'w' in df.at[i, 'sentence_norm']:
        print(i, df.at[i, 'sentence_norm'])
        # print(line, '\t', df.at[i, 'sentence_norm'], '\t', i)

        
"""
import json
metadata = '/home/derik/work/samromur-tools/GetRecordings/output_311220/metadata_2020-12-29.tsv'
df = pd.read_csv(metadata, sep='\t', dtype=str)
df.set_index('id', inplace=True)


done = set()
with open('log/hope_this_works_failed') as f_in:
    for line in f_in:
        line = line.rstrip()
        done.add(line)


with open('reports/report_compined.json') as file:
  data = json.load(file)

for line in data:
    done.add(line['recordingId'])

for i in df.index:
# is_valid != '1.0'
# empty != True, 1
# released != 'V1'

    if df.at[i, 'is_valid'] != '1' \
        and df.at[i, 'empty'] != '1' \
        and df.at[i, 'released'] != 'V1':

        if i not in done:
            print(i)