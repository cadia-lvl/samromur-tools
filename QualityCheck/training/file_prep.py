from os.path import join, exists
from os import makedirs
from os import system


def create_folders_and_files(conf, data_folder, scripts, kaldi_datadir_path):
    steps=join(scripts,'steps')
    utils=join(scripts,'utils')
    if not exists(data_folder):
        makedirs(data_folder)

    if not exists(kaldi_datadir_path):
        makedirs(kaldi_datadir_path)
    
    if not exists(utils):
        system(f'ln -s {conf["kaldi_root"]}/egs/wsj/s5/utils {utils}')
        
    if not exists(steps):
        system(f'ln -s {conf["kaldi_root"]}/egs/wsj/s5/steps {steps}')
    
    if not exists(join(scripts, 'conf')):
        makedirs(join(scripts, 'conf'))
        with open(join(scripts, 'conf', 'mfcc.conf'), 'w') as f_out:
            f_out.write(f'--sample-frequency={conf["sample_rate"]}\n')
            f_out.write('--use-energy=false')     
    
    with open(join(scripts, 'path.sh'), 'w') as f_out:
        f_out.write(f'export KALDI_ROOT={conf["kaldi_root"]}\n')
        f_out.write('export PATH=$KALDI_ROOT/src/ivectorbin:$PWD/utils/:$KALDI_ROOT/src/bin:$KALDI_ROOT/src/chainbin:$KALDI_ROOT/src/online2bin:')
        f_out.write('$KALDI_ROOT/src/onlinebin:$KALDI_ROOT/tools/openfst/bin:$KALDI_ROOT/src/fstbin/:$KALDI_ROOT/src/gmmbin/:$KALDI_ROOT/src/featbin/:')
        f_out.write('$KALDI_ROOT/src/lm/:$KALDI_ROOT/src/sgmmbin/:$KALDI_ROOT/src/sgmm2bin/:$KALDI_ROOT/src/fgmmbin/:$KALDI_ROOT/src/latbin/:')
        f_out.write('$KALDI_ROOT/src/nnet3bin::$KALDI_ROOT/src/nnetbin:$KALDI_ROOT/src/nnet2bin/:$KALDI_ROOT/src/kwsbin:$PWD:$PATH:$KALDI_ROOT/src/fstbin')
        

    with open(join(scripts, 'cmd.sh'), 'w') as f_out:
        f_out.write("export train_cmd=utils/run.pl\n")
        f_out.write("export decode_cmd=utils/run.pl\n")
        f_out.write("export cuda_cmd=utils/run.pl\n")
        f_out.write("export mkgraph_cmd=utils/run.pl")
