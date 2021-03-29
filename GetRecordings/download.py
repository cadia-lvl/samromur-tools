from os.path import join

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
        '-o', '--output', required=False, default='output', type=str, help='Output path')
    
    parser.add_argument(
        '-i', '--ids', required=False, default='recs_to_download.txt', type=str, help='File with a list of ids of recs to get')
    
    parser.add_argument(
        '-m', '--metadata', required=False, default='metadata.tsv', type=str, help='Name of the output metadata file')

    parser.add_argument(
        '-mec', '--metadata_existing_clips', required=False, default=False, type=boolean_string, help='Turns on MEC mode. Gets (M)etadata for all (E)xisting (C)lips. Inspects existings clips afterwards. The download step is skipped.')

    parser.add_argument(
        '-mecp', '--metadata_existing_clips_path', required=False, default=join('output_as_of_050221', 'audio_correct_names'), type=str, help='Path to the root of the clips folder, where the speaker_id folders are located.')

    parser.add_argument(
        '-t', '--threads', required=False, default='5', type=int, help='Number of threads to use when downloading')
    
    parser.add_argument(
        '-or', '--overwrite', required=False, default=False, type=boolean_string, help='Overwrite the output folder')

    # TODO: Add arguments: -v --verbose         help='Print additional data as the script is running.'
    #                      -h --help            help='Some text about what this script does in general.'
    #                      -u --unfetched       help='Scan the database for unfetched data and download it.'

    args = parser.parse_args()

    extractor = Extractor(args)    

    # The download and inspection processes will not start unless the metadata is okay.
    if extractor.get_metadata():
        extractor.download_clips()                                                                                                                                                 
        extractor.inspect_all_audio_files()
        print('\nFinished')