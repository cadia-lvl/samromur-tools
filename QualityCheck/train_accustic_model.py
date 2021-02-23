from training.utils import run_g2p_on_tokens, prep_data, train_acoustic
from config import conf



if __name__ == '__main__':
    
    prep_data(conf)
    
    train_acoustic(conf)