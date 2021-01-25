import random
from tqdm import tqdm
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Set, Dict, Tuple, Optional
import time
import pandas as pd
from collections import Counter


def split_train_test_eval(data, percentage_test, percentage_eval): 
    """ 
    Given a file that contains <id's>\t<sentence>. Returns a dict 
    <id: "test"/"traning"> given a split precentage. The input text 
    is shuffled and no overlap of sentences and speakers in the 
    different sets. 

    """

    spk_ids=[]
    for line in data: 
        spk_ids.append(line[1])

    d = defaultdict(int)
    for w in spk_ids: d[w] += 1 
    x=[]
    for line in data:
        x.append(line + [d[line[1]]])
    
    d = {k:v for k,v in sorted(d.items(), key=lambda items: items[1], reverse=True)}
    data = [v for v in sorted(x, key=lambda x: x[3], reverse=True)]


    distribution = list(d.values())
    print(sum(distribution[0:20]))
    print(distribution[20])
    plt.plot(distribution)
    plt.savefig("distribution.png")

    test_size = int(len(data)*(percentage_test/100))
    eval_size = int(len(data)*(percentage_eval/100))
    training_size = len(data) - test_size - eval_size

    print(f"\nThe total text is {len(data)} lines")
    print(f"The training_size set is {training_size} lines")
    print(f"The test set is {test_size} lines")
    print(f"The eval set is {eval_size} lines\n")


    test_count, eval_count,n, max_rounds = 0, 0, 0, 100
    while (test_count != test_size and eval_count != eval_size) or n <= max_rounds:
        random.seed(n)
        random.shuffle(data)
        test_count, eval_count = 0,0
        status:dict = {}
        test_senteces, eval_senteces, test_spk_id, eval_spk_id = set(), set(), set(), set()

        for line in data:
            key, spk_id, sentece, count = line
            if count >= 100:
               status[key] = 'training'
              
            if sentece not in eval_senteces \
                    and spk_id not in eval_spk_id \
                    and eval_count < eval_size:
                test_senteces.add(sentece)
                test_spk_id.add(spk_id)

                status[key] = 'eval'
                eval_count += 1

            elif sentece not in test_senteces \
                        and sentece not in eval_senteces \
                        and spk_id not in test_spk_id \
                        and spk_id not in eval_spk_id \
                        and test_count < test_size:
                eval_senteces.add(sentece)
                eval_spk_id.add(spk_id)
                 
                status[key] = 'test'
                test_count +=1

                """elif sentece not in test_senteces \
                    and spk_id not in test_spk_id \
                    and test_count < test_size:
                test_senteces.add(sentece)
                test_spk_id.add(spk_id)

                status[key] = 'test'
                test_count +=1

            elif sentece not in test_senteces \
                        and sentece not in eval_senteces \
                        and spk_id not in test_spk_id \
                        and spk_id not in eval_spk_id \https://boardgamearena.com/startwannaplay
                eval_spk_id.add(spk_id) """


            else:
                status[key] = 'training'

        print(f"Eval or test size is not as expected\nTest: {test_count} {test_size}\nEval: {eval_count} {eval_size} ")
        n += 1
        print(n)


    assert test_count == test_size and eval_count == eval_size,\
        print(f"Eval or test size is not as expected\nTest: {test_count} {test_size}\nEval: {eval_count} {eval_size} ")

    return status


