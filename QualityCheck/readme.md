# QualityCheck
This module is used to verify that a given transcription is present in a recording. This module was originally made to work with the data collection platform [Eyra](https://github.com/cadia-lvl/Eyra) but was made a standalone module in the summer of 2020 for verification of the Samrómur recordings. A full list of contributors is available in the Eyra repo as well as a detailed documentation of the implemation in the [developer guide](https://github.com/cadia-lvl/Eyra/blob/master/DEVELOPER.md).


There are two objectives in this module. 
1) To **train a model** to be used for verification.
2) Run the **verification** using the trained model. 

## Table of contents
- [QualityCheck](#qualitycheck)
  - [Table of contents](#table-of-contents)
  - [Model training](#model-training)
    - [Training data](#training-data)
  - [Verification](#verification)
    - [Arguments](#arguments)
  - [Configurations](#configurations)
  - [Installation](#installation)
  - [Workload management](#workload-management)
  - [Acknowledgements](#acknowledgements)

## Model training
All the relevant scripts are located in */training* and can be called with *train_accustic_model.py*. It relies on Kaldi and you can point to your Kaldi installation in config.py. The code is structured in a way that you do not need to be super familiar with Kaldi. 

### Training data
We first need to have the recordings from Samrómur, set the path in config.py. You also need to point to the accompanying metadata file. There should be a column in the metadata which is called *sentence_norm* which is the normalized version of the sentence. This means all lower case, no numerals or signs not in the allowed alphabet.  

The next thing we need is a lexicon file, Google Kaldi lexicon for an example. You should take all the tokens in sentence_norm and create phonetic transcriptions from them. A script for that is available in */training/g2p* but you might have to find the corresponding model elsewhere. Place the lexicon in */training/data*. 

Now you should be able to run train_accustic_model.py. You might however want to add some custom conditions in */training/utils.py* to control which recordings are used to train the model.

When training is done, the relevant output files will be moved to */modules/local* and are ready for use in verification.

## Verification
All scripts regarding verification are located in */modules*. To start the verification, run *runQC.py*. The verification relies on the model trained in */training*. When performing a verification of clips where the numbers are in the range of hundreds of thousands it is highly recommended that you break down your verification batch into smaller subbatches. A recommended subbatch size is 100 - 150 thousand clips. A batch of this size usually takes 2 - 3 days to finish.  The reason this is a good idea is that, assuming you are working on a Linux cluster, there is a chance that the workload managament scheduler will cancel your job if it takes too long. This is also a good working principle in general, to divide and conquer, because you never know what may go wrong.

### Arguments
You may want to tweak the arguments of *runQC.py*. Below are brief explanations of these arguments and their usage. For command examples, please refer to the command history in *runQC_slurm.sh*. 
- `name`
  - Default: `report`
  - An aribitrary value which denotes the session/batch name.
  - If working on many batches, it is recommended to come up with a naming system/convention to clearly denote which batch is which.
    - Example: `100321_qc_100k_218042-1397007` or `<date>_qc_<number-of-clips>_<id-from>-<id-to>`
- `ids`
  - Default: `ids_to_check`
  - A path to a file containing a newline separated list of recording id's for verification.
  - These files should be located in */batches*.
  - It is a good idea to name the file after the batch.
- `batch_size`
  - Default: `20`
  - Used for parallelization. Denotes how many clips a single thread should process at a time.
  - If there comes up some sort of a failure during a verification of a single batch, the whole batch is dropped and the thread skips to next batch. This it is recommended to have this value **low**.
    - Recommended value: `5` 
- `n_jobs`
  - Default: `5`
  - How many threads should be used to perform the verification.
  - A higher number means faster progress on the expense of computation resources.
  - If using a Linux Cluster with the Slurm workload manager, then `n` in `#SBATCH --cpus-per-task=n` should match this value.
  - Recommended value: `12`

## Configurations
Before starting the training or verification process, make sure that everything is properly configured in *config.py*.
- `kaldi_root`
  - Default: `/opt/kaldi`
  - Points to the Kaldi installation you intend to use.
  - The local scripts use Kaldi for training and verification.
- `sample_rate`
  - Default: `16000`
  - The sample rate of the audio data we are working with.
  - Required for the data preparation stage in training.
- `recs`
  - Default: `/work/smarig/h1/samromur-data/as_of_050221/050221_audio_clips/audio_correct_names`
  - Path to the audio recordings.
  - Required in training for access to the training data.
  - Required in verification for access to the data that needs the verification.
- `metadata`
  - Default: `/work/smarig/h1/samromur-data/as_of_050221/050221_metadata/metadata_all_clips_inspect_scored_normalized.tsv`
  - Path to the metadata accompanying the audio recordings.
  - Required in training to acquire the paths, filenames and normalized sentences of the recordings which are to be used for training.
  - Required in verification to acquire id's, transcriptions, paths and filenames of the recordings to verify.
- `g2p_model`
  - Default: ``
  - A path to the G2P model you intend to use to create a lexicon for the model training. 
- `model`
  - Default: `join(getcwd(), 'modules', 'local')`
- `reports_path`
  - Default: `join(getcwd(), 'reports')`

## Installation
The following Python packages are required for this module:
* shortuuid
* sh
* celery

They are also listed in requirements.txt. Therefore, you can easily install all of them by running the command `pip install -r requirements.txt`.

## Workload management
Training models and especially verification of large batches of recordings can become quite time and resource consuming. If you are working on a Linux cluster, it is recommended and encouraged that you use a workload manager such as Slurm. If you are using Slurm, you can perform model training and verification using `train_accustic_model_slurm.sh` and `runQC_slurm.sh`, respectively. You can alter the Slurm parameters at will as well as tweak the Python script arguments in these bash scripts as needed.

## Acknowledgements
"This project was funded by the Language Technology Programme for Icelandic 2019-2023. The programme, which is managed and coordinated by [Almannarómur](https://almannaromur.is/), is funded by the Icelandic Ministry of Education, Science and Culture."