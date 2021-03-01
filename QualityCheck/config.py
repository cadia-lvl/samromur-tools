from os import getcwd
from os.path import join

conf = dict(
    #Needed both for the training and evaluation steps
    kaldi_root = '/home/derik/work/kaldi', 
    sample_rate = 16000,

    #Path to recordings and subsequent metadata file. Used to train the acustic monophone model
    #and can also be used to decode and examine recordings.
    recs = '/work/smarig/h1/samromur-data/as_of_050221/050221_audio_clips/audio_correct_names',
    metadata = '/work/smarig/h1/samromur-data/as_of_050221/050221_metadata/metadata_all_clips_inspect_scored_normalized.tsv',
  
  
    #Variables that you mostlikely wont have to change
    model = join(getcwd(), 'modules', 'local'),
    reports_path = join(getcwd(), 'reports'), 
) 