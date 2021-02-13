# Script maker 

This tool is used to create the script's that are used on (samrómur.is)[www.samromur.is]. It has scripts ready so that it works with the [Icelandix Gigaword Corpus](https://clarin.is/) but is designed to be modular so with relative ease and text could be processed with the tool. We process the text step by step and the output of each step is stored in its own text file. The output are files that contain a <sentences>\t<origin-tag>. The origin tag refers to which subset of the Gigaword corpus the sentence was taken from e.g. Morgunbladid, Althingi etc. 

The scripts made for (Samrómur)[www.samrómur.is] are (https://github.com/aime-island/scripts_for_samromur)

The pipeline is as follows:
* parser.read_corpus() - This step reads through the .xml files found in the Gigaword Corpus.
* parser.parse_text() - Some regex magic to parse the output of the previous step.
* parser.allowed_symbals() - We only keep the sentences that contained our defined allowed characters and symbols.* parser.right_length() - We only keep the sentences that are of the right length, this is a parameter. 
* parser.only_words_in_BIN() - We only keep the sentences that are that contain words that are in BÍN.
* parser.remove_sentences_with_bad_words() - This especially useful for creating scripts for children, we have a list of inappropriate words. 
* parser.right_length_of_word() - We only keep the sentences with words that are of the right length, this is also a parameter.

# Installation
* Python > 3.5
```
pip3 install -r requirements.txt
```
## Resources 
The Icelandic Gigaword Corpus]https://clarin.is/) 

The file KRISTINsnid.csv.zip is available here(https://bin.arnastofnun.is/gogn/mimisbrunnur/) 

create the folder util/data and unzip the file there.

# Running the tool

To read about the parameters run python3 script_maker.py --help
```
python3 create_script.py -rmh <Path-to-the-folder-in the Gigaword corpus> -smin 5 -smax 10 -wmax 10 --code_name test
```

# Authors
Reykjavik University

David Erik Mollberg davidemollberg@gmail.com
