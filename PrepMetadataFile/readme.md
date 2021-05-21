# PrepMetadataFile
This is a collection of tools that are used to prepare downloaded Samrómur data for training or verification. There are tools for sentence normalization, data division into test, train and eval sets and a script for speaker id creation.

## Installation
Make sure to have Python installed, preferably version 3.7.3 or newer. Pandas and Numpy are necessary as well.

## Function and running
This section covers shortly what the tools do and how to run them.


### normalize.py
For a metadata file, runs through its sentence column and normalizes each sentence and puts it into a new column called `sentence_norm`. Writes new metadata file with the additional column for normalized sentences. Additionally adds sentences to a text file (`needs_fixing`) if they contain out of alphabet characters.

`handmade_changes.py` is used by `normalize.py` to "manually" normalize sentences that are known to contain characters or words that are difficult to normalize. These sentences are edge cases which this file takes care of. If you encounter a sentence that is not covered, feel free to add it to this file.

Run simply by entering command: `python3 normalize.py`
For now, it does not accept any parameters and you have to alter a path variable (`path_to_previous_metadata_file`) to point to the desired metadata file.


### split_test_trainV3.py
This script may be used to split a verified corpus into test, train and eval sets.
Run by entering the command `python3 split_test_trainV3.py`
As with `normalize.py`, there are no arguments to give but rather a path which should be modified in the script. The path to the corpus' metadata file, that is. You can also modify the number of recordings you wish to use as well as the ratio of the divided sets.


### create_speaker_id.py
This tool was used to create speaker ids before that value was added to the Samrómur database. The code may give insight on how these ids were generated.


## Authors/Credit
Reykjavik University

- David Erik Mollberg <david.e.mollberg@gmail.com>
- Smári Freyr Guðmundsson <smarig@ru.is>


## Acknowledgements
"This project was funded by the Language Technology Programme for Icelandic 2019-2023. The programme, which is managed and coordinated by [Almannarómur](https://almannaromur.is/), is funded by the Icelandic Ministry of Education, Science and Culture."