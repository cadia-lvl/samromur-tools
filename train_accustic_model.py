from training.utils import normalize_and_prep_data, run_g2p_on_tokens, train_acoustic, create_graphs
from config import conf



if __name__ == '__main__':

    # How many recordings to use to train the acoustic model. None for all of the recordings
    n_acoustic=10000
    
    normalize_and_prep_data(conf, n_acoustic)

    run_g2p_on_tokens()

    train_acoustic(conf)

    create_graphs()