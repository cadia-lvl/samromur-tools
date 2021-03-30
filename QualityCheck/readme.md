# QualityCheck
This module is used to verify that a given transcription is present in a recording. This module was originally made to work with the data collection platform [Eyra](https://github.com/cadia-lvl/Eyra) but was made a standalone module in the summer of 2020 for verification of the Samrómur recordings. A full list of contributors is available in the Eyra repo as well as a detailed documentation of the implemation in the [developer guide](https://github.com/cadia-lvl/Eyra/blob/master/DEVELOPER.md).


There are two objectives in this module. 
1) To **train a model** to be used for verification.
2) Run the **verification** using the trained model. 

## Model training
All the relevant scripts are located in */training* and can be called with *train_accustic_model.py*. It relies on Kaldi and you can point to your Kaldi installation in config.py. The code is structured in a way that you do not need to be super familiar with Kaldi. 

### Training data
We first need to have the recordings from Samrómur, set the path in config.py. You also need to point to the accompanying metadata file. There should be a column in the metadata which is called *sentence_norm* which is the normalized version of the sentence. This means all lower case, no numerals or signs not in the allowed alphabet.  

The next thing we need is a lexicon file, Google Kaldi lexicon for an example. You should take all the tokens in sentence_norm and create phonetic transcriptions from them. A script for that is available in */training/g2p* but you might have to find the corresponding model elsewhere. Place the lexicon in */training/data*. 

Now you should be able to run train_accustic_model.py. You might however want to add some custom conditions in */training/utils.py* to control which recordings are used to train the model.

When training is done, the relevant output files will be moved to */modules/local* and are ready for use in verification.

## Verification
All scripts regarding verification are located in */modules*. They are run using *runQC.py*. 

## Workload management
Training models and especially verification of large batches of recordings can become quite time and resource consuming. If you are working on a Linux cluster, it is recommended that you use workload manager such as Slurm. If you are using Slurm, you can perform model training and verification using `train_accustic_model_slurm.sh` and `runQC_slurm.sh`, respectively. You can alter the Slurm parameters at will as well as tweak the Python script arguments in these bash scripts as needed.