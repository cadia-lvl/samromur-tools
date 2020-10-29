from os import getcwd
from os.path import join

conf = dict(
    kaldi_root = '/home/dem/kaldi', 
    sample_rate = 16000,

    #Batch size when creating graphs and reports.
    batch_size = 100,

    # How many recordings to use to train the acoustic model. None for all avalible
    n_acoustic = 10000 ,

    #Path to recordings and subsequent metadata file. Used to train the acustic monophone model
    #and can also be used to decode and examine recordings.
    recs = '/media/dem/pumba/samromur_v1/audio_16/fixed_header_16000',  
    metadata = '/media/dem/pumba/samromur_v1/metadata.tsv',

    # A g2p model is used in the traning step
    g2p_model ='/home/dem/Projects/samromur-QC/training/data/ipd_clean_slt2018.mdl',
    
    #Variables that you mostlikely wont have to change
    model = join(getcwd(), 'modules', 'local'),
    archive = join(getcwd(), 'recordings'), #Location to store downloaded recordings if applicable
    reports_path = join(getcwd(), 'reports'), 

) 