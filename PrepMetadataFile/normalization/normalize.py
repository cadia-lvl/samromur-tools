from genericpath import exists
from os.path import join
import pandas as pd
from re import sub
import argparse
from pathlib import Path

from handmade_changes import rules

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Normalizes the input metadata file",
        add_help=True,
        formatter_class=argparse.MetavarTypeHelpFormatter,
    )

    def boolean_string(s):
        if s not in {"True", "False"}:
            raise ValueError("Invalid boolean string")
        return s == "True"

    parser.add_argument(
        "-i",
        "--input_metadata",
        required=False,
        default="/home/smarig/work/h1/samromur-data/as_of_050221/050221_metadata/metadata_all_clips_inspect_scored.tsv",
        type=str,
        help="The input metadata file path",
    )

    parser.add_argument(
        "-o",
        "--output_folder",
        required=False,
        default="normalized_files",
        type=str,
        help="The output folder for the normalized files",
    )

    parser.add_argument(
        "-m",
        "--has_marosijo",
        required=False,
        default=True,
        type=boolean_string,
        help="Set this to false if no marosijo scores are available in the metadata",
    )

    args = parser.parse_args()

    def normalize_sentence(s):
        s = s.lower()
        s = s.rstrip()
        s = s.strip()

        s = sub('-', ' ', s)
        s = sub('[!|\.|,|\?|(|)|:|“|„|”|"]', '', s)
        s = s.rstrip()
        return s

    path_to_previous_metadata_file = args.input_metadata

    arch = args.output_folder

    metadata = join(arch, 'metadata.tsv')

    alphabet = 'aábdðeéfghiíjklmnoóprstuúvxyýþæö wzc'

    text = set()

    # v1 = set([str(x.rstrip()).zfill(6) for x in open('/home/derik/work/samromur_validation/validation_V1/v1.ids')])

    df = pd.read_csv(path_to_previous_metadata_file, sep="\t", dtype=str)
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

    if args.has_marosijo:
        df = df[
            [
                "speaker_id",
                "filename",
                "sentence",
                "sentence_norm",
                "gender",
                "age",
                "native_language",
                "dialect",
                "created_at",
                "marosijo_score",
                "released",
                "is_valid",
                "empty",
                "duration",
                "sample_rate",
                "size",
                "user_agent",
            ]
        ]
    else:
        df = df[
            [
                "speaker_id",
                "filename",
                "sentence",
                "sentence_norm",
                "gender",
                "age",
                "native_language",
                "dialect",
                "created_at",
                "released",
                "is_valid",
                "empty",
                "duration",
                "sample_rate",
                "size",
                "user_agent",
            ]
        ]

    # Create the output folder and all parent folders needed
    Path(arch).mkdir(parents=True, exist_ok=True)

    with open(join(arch, 'needs_fixing'), 'w') as f_out:
        for line in text:
            f_out.write(line + '\n')

    df.to_csv(join(arch, 'metadata_normalized.tsv'), header=True, sep='\t', index=True)
