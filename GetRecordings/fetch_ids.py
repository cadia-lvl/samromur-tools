from pathlib import Path

import pandas as pd
from pandas.core.frame import DataFrame
from utils.age_groups import AgeGroups

from modules.database import MySQL
import argparse
import sys


def remove_v1_ids(ids):
    # Import v1 metadata:
    v1_file = "./resources/metadata_v1.tsv"
    v1 = pd.read_csv(v1_file, sep="\t", index_col="id", low_memory=False)
    output = []

    # Add only ids not in v1 to output
    for id in ids:
        if not id["id"] in v1.index:
            output.append(id)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetched the ids of valid clips for the chosen age group. All ages if no age group specified as an input.",
        add_help=True,
        formatter_class=argparse.MetavarTypeHelpFormatter,
    )

    def boolean_string(s):
        if s not in {"False", "True"}:
            raise ValueError("Not a valid boolean string")
        return s == "True"

    parser.add_argument(
        "-o",
        "--output",
        required=False,
        default="clips_ids.csv",
        type=str,
        help="Output filed name",
    )

    parser.add_argument(
        "-ag",
        "--age_group",
        required=False,
        choices=list(item.value for item in AgeGroups),
        default="all",
        type=str,
        help="The specify the agegroup that you want to target. Valid options are 'all', 'kids', 'teens' or 'adults'.",
    )

    parser.add_argument(
        "-x",
        "--exclude_v1",
        required=False,
        default=False,
        type=boolean_string,
        help="Exclude all ids present in the first release.",
    )

    args = parser.parse_args()
    output_file = args.output
    exclude_v1 = args.exclude_v1

    print(f"fetching ids and storing them in: {output_file}")

    # Check if input age group is a valid entry
    try:
        age_group = AgeGroups(args.age_group)

    except Exception as e:
        print(
            f"ERROR: Age group: '{args.age_group}' is not a valid age group. Valid age groups are: 'all','kids','teens' and 'adults'. \nExiting..."
        )
        print(e)
        sys.exit(1)

    if Path(output_file).exists():
        print(
            f"ERROR: The output file: '{output_file}' already exists, please choose a new one or delete the existing one."
        )
        sys.exit(1)

    sql = MySQL(ids_to_get=[])
    ids = sql.get_all_is_valid_ids(age_group)

    if exclude_v1:
        ids = remove_v1_ids(ids)

    if not Path(output_file).parent.exists():
        Path(output_file).parent.mkdir(parents=True)

    with open(output_file, "w") as f:
        for row in ids:
            f.write(f'{row["id"]}\n')
