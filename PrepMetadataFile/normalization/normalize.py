from os.path import join
import pandas as pd
from re import sub

from handmade_changes import rules

def normalize_sentence(s):
    s = s.lower()
    s = s.rstrip()
    s = s.strip()

    s = sub('-', ' ', s)
    s = sub('[!|\.|,|\?|(|)|:|“|„|”|"]','', s)
    s = s.rstrip()
    return s

path_to_previous_metadata_file = '/home/smarig/work/h1/samromur-data/as_of_050221/050221_metadata/metadata_all_clips_inspect_scored.tsv'

arch = 'normalized_files'

metadata = join(arch, 'metadata.tsv')

alphabet = 'aábdðeéfghiíjklmnoóprstuúvxyýþæö wzc'

text = set()

#v1 = set([str(x.rstrip()).zfill(6) for x in open('/home/derik/work/samromur_validation/validation_V1/v1.ids')])

df = pd.read_csv(path_to_previous_metadata_file, sep='\t', dtype=str)
df.set_index('id', inplace=True)
df['released'] = 'NAN'

for i in df.index:
    s = normalize_sentence(df.at[i, 'sentence'])
    s = rules(s)
    df.at[i, 'sentence_norm'] = s
    #To find the sentene outside of the vocabulary
    for l in s:
        if l not in alphabet:
            text.add(s)

    #if i in v1:
    #   df.at[i, 'released'] = 'V1'

df = df[['speaker_id', 'filename', 'sentence', 'sentence_norm', 'gender', 'age', 'native_language', 'dialect', 'created_at', \
         'marosijo_score', 'released', 'is_valid', 'empty', 'duration', 'sample_rate', 'size', 'user_agent']]

with open(join(arch, 'needs_fixing'), 'w') as f_out:
    for line in text:
        f_out.write(line+'\n')

df.to_csv(join(arch, 'metadata.tsv'), header=True, sep='\t', index=True)
