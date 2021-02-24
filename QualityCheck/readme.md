# Quality Ckeck

This modules is used to verify that a given transcription is present in a recordings. This module was orginally made to work with the data collection platfrom [Eyra](https://github.com/cadia-lvl/Eyra). But it was made a standalone module in the summer of 2020 for verfication of the Samrómur recordings. A full list of contributers is avalible in the Eyra repo as well as a detailed documentation of the implemation in the [developer guide](https://github.com/cadia-lvl/Eyra/blob/master/DEVELOPER.md).


There are two objectives in this module. Firstly to train a model and then to run the model. 

# Train the model 

All the relevant scripts are located in */training* and can be called with *train_accustic_model.py*. It relies on Kaldi and you can point to your Kaldi installation in config.py. The code is structured in a way that you do not need to be super familiar with Kaldi. 


## Data needed for training 
We first need to have the recordings from Samrómur, set the path in config.py. You also need to point to the accompanying metadata file. There should be a column in the metadata which is called *sentence_norm* which is the normalized version of the sentence. This means all lower case, no numerals or signs not in the allowed alphabet.  

The next thing we need is a lexicon file, google Kaldi lexicon for an example. You should take all the tokens in sentence_norm and create phonetic transcriptions from them. A script for that is available in */training/g2p* but you might have to find the corresponding model elsewhere. Place the lexicon in */training/data*. 

Now you should be able to run train_accustic_model.py. You might however want to add some custom conditional in */training/utils.py* to control what clips recordings are used to train the model.

When training is done the relevant output files will be moved to */modules/local* and are ready for use.

# Run QC
