from os import getcwd
from os.path import join

conf = dict(
    kaldi_root = '/home/dem/kaldi', 
    archive = 'recordings', #Location to store downloaded recordings if applicable
    reports_path = 'reports', 

    sample_rate = 16000,

    
    #Variables used to train the acustic monophone model
    recs = '/media/dem/pumba/samromur_v1/audio_16/fixed_header_16000',  
    g2p_model ='/home/dem/Projects/samromur-QC/training/data/ipd_clean_slt2018.mdl',
    metadata = '/media/dem/pumba/samromur_v1/metadata.tsv',
    model=join(getcwd(), 'modules', 'local')
) 