from os import getcwd
from os.path import join

conf = dict(
    #Needed both for the training and evaluation steps
    kaldi_root = '/opt/kaldi', 
    sample_rate = 16000,

    # How many recordings to use to train the acoustic model. None for all avalible
    n_acoustic = 10000,

    #Path to recordings and subsequent metadata file. Used to train the acustic monophone model
    #and can also be used to decode and examine recordings.
    recs = '/data/asr/samromur/samromur_v1/samromur_v1/audio/',  
    metadata = '/data/asr/samromur/samromur_v1/samromur_v1/metadata.tsv',

    # A g2p model is used in the traning step
    g2p_model ='training/data/ipd_clean_slt2018.mdl',
    
    #Variables that you mostlikely wont have to change
    model = join(getcwd(), 'modules', 'local'),
    reports_path = join(getcwd(), 'reports'), 
) 