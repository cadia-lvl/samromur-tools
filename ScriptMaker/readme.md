# Script maker 

This tool is used to create the script's that are used on samromur.is. It has scripts ready so that it works with the [Icelandix Gigaword Corpus](https://clarin.is/) but is designed to be modulor so with relative ease and text could be processed with the tool. We process the text step by step and the output of each step is stored in it's own text file. The output are files that contain a <sentences>\t<origin-tag>. The origin tag refers to which subest of the Gigaword corpus the sentence was taken from e.g. Morgunbladid, Althingi etc. 
	
The scripts made for Samrómur are located in this [repo](https://github.com/aime-island/scripts_for_samromur)

The pipeline is as follows:
    parser.read_corpus() - This step reads through the .xml files found in the Gigaword Corpus.
    parser.parse_text() - Some regex magic to parse the output of the previous step.
    parser.allowed_symbals() - We only keep the sentences that contained our defiened allowd charachtes and symbols.
    parser.right_length() - We only keep the sentences that are of the right lenght, this is parameter. 
    parser.only_words_in_BIN() - We only keep the sentences that are that contain words that are in BÍN.
    parser.remove_sentences_with_bad_words() - This espceially useful for creating scripts for children, we have a list of inapproppriate words. 
    parser.right_length_of_word() - We only keep the sentences with words that are of the right length, this is also parameter.

# Installation
* Python > 3.5
```
pip3 install -r requirements.txt
```
## Resources 
The Icelandix Gigaword Corpus]https://clarin.is/) 

The file KRISTINsnid.csv.zip is avalible here(https://bin.arnastofnun.is/gogn/mimisbrunnur/) 

create the folder util/data and unzip the file there.

# Running this tool
Have a look at the parameters in util/argparser.py. 

Example run: 
```
python3 create_script.py -rmh /data/text/risamalheild/2018/rmh1/andriki/ -smin 3 -smax 10 -wmax 4 -code_name test
```

# Authors/Credit
Reykjavik University

David Erik Mollberg davidemollberg@gmail.com
