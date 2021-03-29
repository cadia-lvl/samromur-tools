from os.path import join
from tqdm import tqdm
import pandas as pd
import os
from re import sub
import subprocess


from training.file_prep import create_folders_and_files

data_folder=join(os.getcwd(),'training','data')
scripts=join(os.getcwd(),'training', 'scripts')

kaldi_datadir_path=join(scripts, 'data', 'all')
token_file=join(data_folder, 'tokens.txt')
lexicon_file=join(data_folder, 'lexicon.txt')
phonemes_file=join(data_folder, 'phonemes.txt')


def prep_data(conf, ids):
    '''
    Prep Kaldi files.
    '''

    create_folders_and_files(conf, data_folder, scripts, kaldi_datadir_path)

    text = open('{}/text'.format(kaldi_datadir_path), 'w')
    wavscp = open('{}/wav.scp'.format(kaldi_datadir_path), 'w')
    utt2spk = open('{}/utt2spk'.format(kaldi_datadir_path), 'w')
    spk2utt = open('{}/spk2utt'.format(kaldi_datadir_path), 'w')

    tokens = set()
    df = pd.read_csv(join(conf['metadata']), sep='\t', dtype='str')

    # Filter ids by ids in id file.
    df_acoustic = df[df['id'].isin(ids)]
    print(f"{len(df_acoustic)} being used for acoustic training")

    df.set_index('id', inplace=True)
    df_acoustic.set_index('id', inplace=True)
    for i in tqdm(df_acoustic.index, unit='lines'):
        utt_id = df.at[i, 'filename'][:-4]
        full_rec_path = join(conf['recs'], df.at[i, 'speaker_id'], df.at[i, 'filename'])
        print(utt_id, df.at[i, 'sentence_norm'], file=text)
        print(f'{utt_id} sox - -c1 -esigned -r {conf["sample_rate"]} -twav - < {full_rec_path} | ', file=wavscp)
        print(f"{utt_id} {df.at[i, 'speaker_id']}", file=utt2spk)

    text.close()
    wavscp.close()
    utt2spk.close()

    df_acoustic.to_csv(join(data_folder, 'metadata_accoustic.tsv'), sep='\t')

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


def train_acoustic(conf):
    create_phonemes_file()
    create_folders_and_files(conf, data_folder, scripts, kaldi_datadir_path)
    subprocess.call(f"{join(scripts, 'train_mono_phone.sh')} {lexicon_file} {phonemes_file} {conf['model']}", cwd=scripts, shell=True)
