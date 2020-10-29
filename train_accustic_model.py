from training.utils import normalize_and_prep_data, run_g2p_on_tokens, train_acoustic
from config import conf



if __name__ == '__main__':

    
    #normalize_and_prep_data(conf)

    #run_g2p_on_tokens(conf)

    train_acoustic(conf)