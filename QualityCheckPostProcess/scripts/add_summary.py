from os import sep
from os.path import join
from tqdm import tqdm

"""Put n summaries together into one file."""

"""Taken from stats_tools/stats.py. Use this function to finish this script."""
def add_summaries(summary_path_lis):
    """ Takes a list of paths to summaries (or a single one) and returns the summaries in a map like this: [id]->marosijo_score """

    # Put into a single element list if only one argument is passed in.
    summary_path_lis = [summary_path_lis] if type(summary_path_lis) != list else summary_path_lis

    sum_dic = {}

    for path in tqdm(summary_path_lis):
        with open(path) as f_in:
            for line in f_in:
                cols = line.split('\t')
                sum_dic[cols[0]] = cols[1].strip()
                
    return sum_dic


dir_lis:list = [                                                                                                                                \
    join(sep, 'home', 'smarig', 'work', 'h1', 'samromur-verification-wrapup', 'marosijo_scores', 'original', '190221_qc_big_summary.tsv'),                   \
    join(sep, 'home', 'smarig', 'work', 'h1', 'samromur-verification-wrapup', 'marosijo_scores', 'original', '240221_qc_first_200k_summary.tsv'),            \
    join(sep, 'home', 'smarig', 'work', 'h1', 'samromur-verification-wrapup', 'marosijo_scores', 'original', '260221_qc_150k_218042-895299_summary.txt'),    \
    join(sep, 'home', 'smarig', 'work', 'h1', 'samromur-verification-wrapup', 'marosijo_scores', 'original', '010321_qc_150k_218042-1099684_summary.tsv'),   \
    join(sep, 'home', 'smarig', 'work', 'h1', 'samromur-verification-wrapup', 'marosijo_scores', 'original', '040321_qc_100k_218042-1192490_summary.txt'),   \
    join(sep, 'home', 'smarig', 'work', 'h1', 'samromur-verification-wrapup', 'marosijo_scores', 'original', '080321_qc_100k_218042-1336566_summary.txt'),   \
    join(sep, 'home', 'smarig', 'work', 'h1', 'samromur-verification-wrapup', 'marosijo_scores', 'original', '100321_qc_42k_218042-1397007_summary.txt')    \
]

score_dic:dict = add_summaries(dir_lis)

with open('marosijo_summary_all.tsv', 'a') as f_in:
    for key, val in score_dic.items():
        f_in.write(f'{key}\t{val}\n')

print(f'Finished writing {len(score_dic)} id-score pairs to marosijo_summary_all.tsv')