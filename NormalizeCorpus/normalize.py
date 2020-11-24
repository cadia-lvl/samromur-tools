import tokenizer
from os.path import join, basename
from re import sub
from tqdm import tqdm
import pandas as pd
from re import sub

from handmade_changes import rules
from split_test_train import split_train_test_eval

def normalize_sentence(s):
    s = s.lower()
    s = s.rstrip()
    s = s.strip()

    s = sub('-', ' ', s)
    s = sub('[!|\.|,|\?|(|)|:|“|„|”|"]','', s)
    s = s.rstrip()
    return s

path_to_metadata = '/data/samromur/samromur_v1/samromur_v1/metadata.tsv'

arch = 'normalized_files'
precentage_test:int = 10
precentage_eval:int = 2.5

metadata = join(arch, 'metadata.tsv')
text_file = join(arch, 'text') 
tokens_file = join(arch, 'tokens.txt')

alphabet = 'aábdðeéfghiíjklmnoóprstuúvxyýþæö wzc'

text, tokens = [], set()
df = pd.read_csv(path_to_metadata, sep='\t', index_col='id')
for i in tqdm(df.index, unit='lines'):
        s = normalize_sentence(df.at[i, 'sentence'])
        s = rules(s)
        df.at[i, 'sentence_norm'] = s
        text.append([i,s])
        for tok in s.split(' '):
            tokens.add(tok)
        
        #To find the sentene outside of the vocabulary
        #for l in new_string:
        #    if l not in alphabet:
        #        print(new_string) 
          
status = split_train_test_eval(text, precentage_test, precentage_eval)
for i in tqdm(df.index, unit='lines'):
    df.at[i, 'status'] = status[i]

df = df[['filename', 'speaker_id', 'sex', 'age', 'native_language',\
     'duration', 'sample_rate', 'sentence', 'sentence_norm', 'status', 'released']]

df.to_csv(join(arch, 'metadata.tsv'), sep='\t', index=True)

with open(text_file, 'w') as text_out:
    with open(join(arch, 'samromur_corpus.txt'), 'w') as corpus_out:   
        for line in sorted(text, key=lambda x: x[0]):
            corpus_out.write(line[1]+'\n')
            text_out.write(str(line[0])+'\t'+line[1]+'\n')

with open(tokens_file, 'w') as tok_out:
    for tok in sorted(list(tokens)):
        if len(tok) >0:
            tok_out.write(tok+'\n')


