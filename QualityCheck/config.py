from os import getcwd
from os.path import join

conf = dict(
    #Needed both for the training and evaluation steps
    kaldi_root = '/opt/kaldi', 
    sample_rate = 16000,

    #Path to recordings and subsequent metadata file. Used to train the acustic monophone model
    #and can also be used to decode and examine recordings.
    recs = '/home/derik/work/samromur-tools/GetRecordings/output_311220/audio_correct_names',  
    metadata = '/home/derik/work/samromur-tools/GetRecordings/output_311220/metadata_2020-12-29.tsv',

    # A g2p model is used in the traning step
    g2p_model ='training/data/ipd_clean_slt2018.mdl',
    
    #Variables that you mostlikely wont have to change
    model = join(getcwd(), 'modules', 'local'),
    reports_path = join(getcwd(), 'reports'), 
) 