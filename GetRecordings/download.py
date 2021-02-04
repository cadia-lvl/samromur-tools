from modules.extractor import Extractor
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Download clips and parse metadata',
        add_help=True,
        formatter_class=argparse.MetavarTypeHelpFormatter)

    def boolean_string(s):
        if s not in {'False', 'True'}:
            raise ValueError('Not a valid boolean string')
        return s == 'True'

    parser.add_argument(
        '-o', '--output', required=False, default='output', type=str, help='output path')
    
    parser.add_argument(
        '-i', '--ids', required=False, default='recs_to_download.txt', type=str, help='File with a list of ids of recs to get')
    
    parser.add_argument(
        '-m', '--metadata', required=False, default='metadata.tsv', type=str, help='Name of the metadata file')

    parser.add_argument(
        '-t', '--threads', required=False, default='5', type=int, help='Number of threads to use when downloading')
    
    parser.add_argument(
        '-or', '--overwrite', required=False, default=False, type=boolean_string, help='Overwrite the output folder')

    # TODO: Add arguments: -v --verbose and -h --help. 

    args = parser.parse_args()

    extractor = Extractor(args)    
    extractor.get_metadata()
    extractor.download_clips_parallel()                                                                                                                                                 
    extractor.inspect_all_audio_files()