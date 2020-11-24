from os.path import join
from tqdm import tqdm
import pandas as pd
import os
from re import sub
import subprocess


from training.normalize_samromur import normalize_sentence
from training.file_prep import create_folders_and_files

data_folder=join(os.getcwd(),'training','data')
scripts=join(os.getcwd(),'training', 'scripts')

kaldi_datadir_path=join(scripts, 'data', 'all')
token_file=join(data_folder, 'tokens.txt')
lexicon_file=join(data_folder, 'lexicon.txt')
phonemes_file=join(data_folder, 'phonemes.txt')


def normalize_and_prep_data(conf, n_acoustic):
    '''
    Normalize the text and prep files.
    '''

    create_folders_and_files(conf, data_folder, scripts, kaldi_datadir_path)
    alphabet = 'aábdðeéfghiíjklmnoóprstuúvxyýþæö wzqc'

    text = open('{}/text'.format(kaldi_datadir_path), 'w')
    wavscp = open('{}/wav.scp'.format(kaldi_datadir_path), 'w')
    utt2spk = open('{}/utt2spk'.format(kaldi_datadir_path), 'w')
    spk2utt = open('{}/spk2utt'.format(kaldi_datadir_path), 'w')

    tokens = set()

    df = pd.read_csv(join(conf['metadata']), sep='\t', index_col='id')

    if conf['n_acoustic']:
        #Variables to limit the acustic data used. 
        n = [conf['n_acoustic'], True, 1]
    else:
        n = [1, False, 0]
        
    for i in tqdm(df.index, unit='lines'):
        df.at[i, 'sentence'] = normalize_sentence(df.at[i, 'sentence'])

        for tok in df.at[i, 'sentence'].split(' '):
            tokens.add(tok)

        if n[2] <= n[0]:
            utt_id = '{}-{}'.format(df.at[i, 'speaker_id'], i)
            full_rec_path = join(conf['recs'], df.at[i, 'filename'])
            print(utt_id, df.at[i, 'sentence'], file=text)
            print(f'{utt_id} sox - -c1 -esigned -r {conf["sample_rate"]} -twav - < {full_rec_path} | ', file=wavscp)
            print(utt_id, str(df.at[i, 'speaker_id']), file=utt2spk)

        if n[1]:
            n[2] += 1


    text.close()
    wavscp.close()
    utt2spk.close()

    df.to_csv(join(data_folder, 'metadata.tsv'), sep='\t', index=False)

    with open(token_file, 'w') as f_out:
        for tok in sorted(list(tokens)):
            if len(tok) > 0:
                f_out.write(tok+'\n')

    #We need to change location to run a sub script
    data = 'data/all'
    subprocess.call(f'utils/utt2spk_to_spk2utt.pl < {data}/utt2spk > {data}/spk2utt', cwd=scripts, shell=True)
    subprocess.call(f'utils/validate_data_dir.sh --no-feats {data} || utils/fix_data_dir.sh {data}', cwd=scripts, shell=True)

    spk2utt.close()

def create_phonemes_file():
    with open(phonemes_file, 'w') as f_out:
        with open(lexicon_file) as f_in:
            phones = set()
            for line in f_in:
                line = sub('^.*\t','', line.rstrip())
                for p in line.split(' '):
                    phones.add(p)
        for phone in sorted(list(phones)):
            f_out.write(phone+'\n')


def run_g2p_on_tokens(conf):
    subprocess.call(f"g2p.py --apply {token_file} --model {conf['g2p_model']} --encoding='UTF-8' > {lexicon_file}", shell=True)
    create_phonemes_file()

def train_acoustic(conf):
    create_folders_and_files(conf, data_folder, scripts, kaldi_datadir_path)
    subprocess.call(f"{join(scripts, 'train_mono_phone.sh')} {lexicon_file} {phonemes_file} {conf['model']}", cwd=scripts, shell=True)
