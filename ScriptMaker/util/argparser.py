import argparse

def create_parser():
    parser = argparse.ArgumentParser(
        description='Text exctractor for althingi speeches',
        add_help=True,
        formatter_class=argparse.MetavarTypeHelpFormatter)

    parser.add_argument(
        '-rmh', '--process_rmh', required=False, default=None, type=str, help='path to data folder to extract')

    parser.add_argument(
        '-t', '--process_text', required=False, default=None, type=str, help='path to data text file to be normalized')

    parser.add_argument(
        '-o', '--output_folder', required=False, default='results', type=str, help='path to output folder')

    parser.add_argument(
        '-n', '--n_jobs', required=False, type= int, default=1, help='Count of how many parallel jobs')

    parser.add_argument(
        '-bw', '--bad_words_path', required=False, type= str, help='Path to file with bad words')

    parser.add_argument(
        '-smin', '--s_min', required=False, type= int, default=2, help='Minnimum length of sentences')

    parser.add_argument(
        '-smax', '--s_max', required=False, type= int, default=15, help='Maximum length of sentences')

    parser.add_argument(
        '-wmax', '--w_max', required=False, type= int, default=35, help='Maximum length of word')

    parser.add_argument(
        '-f', '--file_type', required=False, type= str, default='.tsv', help='write the file type extension\ne.g. .tsv, .txt, .csv ')

    parser.add_argument(
        '-c', '--code_name', required=False, type= str, default=None, help='The name of the output file that will get concactenated with the actions taken')

    return parser