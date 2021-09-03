""" 
1. [x] Update vote information in main metadata file
2. [] Run this script
3. [] Put number of manually verified clips into Venn diagrams
4. [] Add machine_verified boolean column to metadata
5. [] Add votes to database
6. [] Update local metadata
7. [] Write report
"""

from collections import defaultdict
from os.path import exists
from os import remove
from tqdm import tqdm

import pandas as pd
import argparse


OUTPUT_HEADER:str = 'id\tpos_vote\tneg_vote\tsuper\tscore_group\tempty\tmfa_unalignable\tmarosijo_score'
REPORT_HEADER:str = 'score_group\tmarosijo_vote_amount\tman_verification_amount'

# Score groups
SCORE_HIGH:str = 'high'                             # 0.900 - 1.000
SCORE_BETWEEN:str = 'between'                       # 0.301 - 0.899
SCORE_LOW:str = 'low'                               # 0.001 - 0.300
SCORE_LOW_UNALIGNABLE:str = 'low_unalignable'       # 0.001 - 0.300 & MFA unalignable
SCORE_ZERO:str = 'zero'                             # 0.000

# Other groups
EMPTY:str = 'empty'                                 # Should all be without Marosijo scores (nonverified) - There may be clips which slipped through though
NONVERIFIED:str = 'nonverified'                     # Should all be marked empty - Exception: Clips that Marosijo was unable to verify for some reason, they are nonverified and nonempty

# Vote map defines the votes for score groups
vote_map:dict = {
    SCORE_HIGH: {
        'POSITIVE': 1,
        'NEGATIVE': 0,
        'SUPER': 0
    },
    SCORE_LOW: {
        'POSITIVE': 0,
        'NEGATIVE': 1,
        'SUPER': 0
    },
    SCORE_LOW_UNALIGNABLE: {
        'POSITIVE': 0,
        'NEGATIVE': 1,
        'SUPER': 1
    },
    SCORE_ZERO: {
        'POSITIVE': 0,
        'NEGATIVE': 1,
        'SUPER': 1
    },
    EMPTY: {
        'POSITIVE': 0,
        'NEGATIVE': 1,
        'SUPER': 1
    },
    NONVERIFIED: {
        'POSITIVE': 0,
        'NEGATIVE': 0,
        'SUPER': 0
    },
    SCORE_BETWEEN: {
        'POSITIVE': 0,
        'NEGATIVE': 0,
        'SUPER': 0
    }
}

def get_score_group(score, is_empty, unalignable):
    # As a good practice, Marosijo should be fed with ids of clips that have been inspected by inspect_all_audio_files() in
    # Samromur-tools/modules/extractor.py and marked as nonempty. That leaves a good portion of empty clips which are nonverified
    # and lack scores therefore. These empty-marked clips go to the EMPTY score group and get an automatic negative super vote.
    if is_empty == '1': return EMPTY
    
    # There may be instances of clips that are nonempty and nonverified, e.g. when Marosijo has been given a batch of clips marked
    # as nonempty but is unable to verify some of them for some reason. These clips are not a given negative nor a positive vote. 
    elif score == 'NAN': return NONVERIFIED


    score_f:float = float(score)

    # Zero scoring clips have been proven to be unusable and go to the SCORE_ZERO score group where they receive a negative super vote.
    if score_f == 0: return SCORE_ZERO

    # Clips on the range of 0.01 - 0.3 go to the SCORE_LOW score group where they receive a negative vote. They do not get a super vote
    # as there is always a considerable chance of false negatives in the score of that range.
    elif 0 < score_f <= 0.3:

        # If, however, a clip is in this range AND Montreal Forced Aligner (MFA) has failed to align it, it is most likely bad and is put into
        # the SCORE_LOW_UNALIGNABLE score group and receives a negative super vote. 
        # NOTE: To get this list, the ids of clips scoring from 0.01 - 0.3 (SCORE_LOW) are put into MFA alignment and one of its output files
        # (output/unaligned.txt) contains the ids of clips that were unalignable due to being of extremly poor quality or containing only noise.
        if unalignable: return SCORE_LOW_UNALIGNABLE

        return SCORE_LOW

    # Clips on the range of 0.9 - 1.0 go to the SCORE_HIGH score group where they receive a positive vote. They do not get a super vote
    # as there is always a considerable chance of false positives in the score of that range.
    elif score_f >= 0.9: return SCORE_HIGH

    # The clips that score between 0.301 and 0.899 are the clips that we do not confidently trust to let Marosijo decide the fate of. After a manual
    # evaluation of the legitimacy of Marosijo scores, it has been proven that clips on that range are often very good but also often very bad. 
    # Therefore they go to the SCORE_BETWEEN score group where the don't receive a negative nor a positive vote.
    elif 0.3 < score_f < 0.9: return SCORE_BETWEEN

    # If none of the above criteria are met, something is incorrect in the metadata.
    else: raise Exception()

def generate_marosijo_scores(metadata, fname_output, fname_report, unalignable_lis):
    if exists(fname_output):
        print(f'Output file with the name \"{fname_output}\" already exists. Please pick another name or delete the other one first.\nTerminating script...')
        return
    elif exists(fname_report):
        print(f'Report file with the name \"{fname_report}\" already exists. Please pick another name or delete the other one first.\nTerminating script...')
        return

    # Stats counting maps for the report
    nonverified_vote_count_map:defaultdict = defaultdict(int)
    man_vote_count_map:defaultdict = defaultdict(int)

    success:bool = True
    failed_id:str = ''
    metadata.set_index('id', inplace=True)
    with open(fname_output, 'a') as output_fin:
        print(f'Creating file(s) in current working directory:\nOutput file: {fname_output}')

        output_fin.write(f'{OUTPUT_HEADER}\n')

        print('Parsing files and generating output...')
        for id in tqdm(metadata.index):
            meta_is_valid:str        = metadata.at[id, 'is_valid']
            meta_empty:str           = metadata.at[id, 'empty']
            meta_marosijo_score:str  = metadata.at[id, 'marosijo_score']

            unalignable:bool = id in unalignable_lis

            try:
                score_group:str = get_score_group(meta_marosijo_score, meta_empty, unalignable)
            except:
                failed_id = id
                success = False
                break

            # We are only interested in clips that are non-verified.
            if meta_is_valid == 'NAN':
                vote_data = vote_map[score_group]
                output_fin.write(f'{id}\t{vote_data["POSITIVE"]}\t{vote_data["NEGATIVE"]}\t{vote_data["SUPER"]}\t{score_group}\t{meta_empty}\t{unalignable}\t{meta_marosijo_score}\n')
                
                # We count how many non-manually verified clips received votes
                nonverified_vote_count_map[score_group] += 1

            # We want to count the clips which have already been manually verified. These might have Marosijo scores, or not (like the empty clips which are not Marosijo verified)
            else:
                man_vote_count_map[score_group] += 1

    if success:
        generate_report(fname_report, nonverified_vote_count_map, man_vote_count_map)
        print(f'Finished successfully!\nOutput files created in current working directory:\nOutput: {fname_output}\nStatistics report: {fname_report}\n\nExiting...')
    else:
        print(f'Failed to determine scoregroup for clip: {failed_id}\n Deleting unfinished output files and terminating script...')
        remove(fname_output)

def generate_report(fname_report, nonverified_vote_count_map, man_vote_count_map):
    with open(fname_report, 'a') as report_fin:
        print(f'Creating file(s) in current working directory:\nStatistics report file: {fname_report}')

        report_fin.write(f'{REPORT_HEADER}\n')

        report_fin.write(f'{SCORE_HIGH}\t{nonverified_vote_count_map[SCORE_HIGH]}\t{man_vote_count_map[SCORE_HIGH]}\n')
        report_fin.write(f'{SCORE_BETWEEN}\t{nonverified_vote_count_map[SCORE_BETWEEN]}\t{man_vote_count_map[SCORE_BETWEEN]}\n')
        report_fin.write(f'{SCORE_LOW}\t{nonverified_vote_count_map[SCORE_LOW]}\t{man_vote_count_map[SCORE_LOW]}\n')
        report_fin.write(f'{SCORE_LOW_UNALIGNABLE}\t{nonverified_vote_count_map[SCORE_LOW_UNALIGNABLE]}\t{man_vote_count_map[SCORE_LOW_UNALIGNABLE]}\n')
        report_fin.write(f'{SCORE_ZERO}\t{nonverified_vote_count_map[SCORE_ZERO]}\t{man_vote_count_map[SCORE_ZERO]}\n')
        report_fin.write(f'{EMPTY}\t{nonverified_vote_count_map[EMPTY]}\t{man_vote_count_map[EMPTY]}\n')
        report_fin.write(f'{NONVERIFIED}\t{nonverified_vote_count_map[NONVERIFIED]}\t{man_vote_count_map[NONVERIFIED]}\n')

        # Report explanation
        # Number of Marosijo votes / manual verifications of clips within the score range of 0.9 - 1.0
        # Number of Marosijo votes / manual verifications of clips within the score range of 0.301 - 0.899 (between low and high scores)
        # Number of Marosijo votes / manual verifications of clips within the score range of 0.01 - 0.3
        # Number of Marosijo votes / manual verifications of clips within the score range of 0.01 - 0.3 and are MFA unalignable.
        # Number of Marosijo votes / manual verifications of clips with the score of 0
        # Number of Marosijo votes / manual verifications of clips marked empty (Usually empty and non-verified as well)
        # Number of Marosijo votes / manual verifications of clips that were not verified by Marosijo (non-empty clips that were not verified for some reason)

def get_metadata_df(metadata_path): 
    df = pd.read_csv(metadata_path, sep='\t', dtype=str)
    print(f'Found a metadata file containing {len(df)} clip entries...')
    return df

def get_mfa_unaligned_list(path_to_unaligned_list):
    unaligned_lis = []

    with open(path_to_unaligned_list, 'r') as f_in:
        for line in f_in:
            unaligned_lis.append(line
                .split("\t")[0]
                .split("-")[1]
                .strip()
            )
    
    print(f'Found a list of {len(unaligned_lis)} ids of unalignable clips...')
    return unaligned_lis

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="""This tool generates votes for Samrómur recordings based on their Marosijo scores.""",
        add_help=True,
        formatter_class=argparse.MetavarTypeHelpFormatter)
    
    parser.add_argument(
        '-m', '--metadata', required=False, default='/work/smarig/h1/samromur-data/as_of_050221/metadata.tsv', type=str, help='Path to main metadata file')

    parser.add_argument(
        '-mfa', '--mfa', required=False, default='/work/smarig/h1/samromur-verification-wrapup/mfa/unaligned.txt', type=str, help='Path to a file containing Montreal Forced Aligner\'s list of unalignable clips')

    parser.add_argument(
        '-o', '--output', required=False, default='output_votes.tsv', type=str, help='Name of output file with vote data')

    parser.add_argument(
        '-r', '--report', required=False, default='stats_report.tsv', type=str, help='Name of output report file with statistics')

    args = parser.parse_args()

    generate_marosijo_scores(get_metadata_df(args.metadata), args.output, args.report, get_mfa_unaligned_list(args.mfa))

    # TODO: Add an option to NOT to have MFA list of unalignable clips. Make it optional.