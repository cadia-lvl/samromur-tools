import pandas as pd
from collections import defaultdict
from tqdm import tqdm

input_metadata:str = '/home/derik/work/samromur_validation/samromur_wip/metadata_speaker_id.tsv'

df = pd.read_csv(input_metadata, sep='\t')
print(df.head())
spks:dict = {}
id =1
for i in tqdm(df.index):
    combination = f"{df.at[i, 'client_id']}/{df.at[i, 'age']}/{df.at[i, 'gender']}/{df.at[i, 'native_language']}"	
    if combination not in spks.keys():
        spks[combination] = id
        id += 1

for i in tqdm(df.index):
    combination = f"{df.at[i, 'client_id']}/{df.at[i, 'age']}/{df.at[i, 'gender']}/{df.at[i, 'native_language']}"	
    df.at[i, 'new_spks'] = spks[combination]


df.to_csv('metadata_total_041220_new_spks.tsv', sep='\t')

print(f"The number of unique speakers is {len(spks.values())}")
