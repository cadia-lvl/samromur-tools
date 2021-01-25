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
    '''
    Let's loop through the data using a greedy algorithm. 
    '''

    start = time.time()
    max_value = [0,0,0]
    max_value[1] = int(len(data)*(percentage_test/100))
    max_value[2] = int(len(data)*(percentage_eval/100))
    max_value[0] = len(data) - max_value[1] - max_value[2]

    print(f"\nThe total text is {len(data)} lines")
    print(f"The training_size set is {max_value[0]} lines")
    print(f"The test set is {max_value[1]} lines")
    print(f"The eval set is {max_value[2]} lines\n")

    total_penalty = 0
    """Each dict has set for the speaker_id, senteces, penalty and  count inn that order"""
    sets:dict = {'training':[set(), set(), 0, []], \
                 'test':[set(), set(), 0, []], \
                 'eval':[set(), set(), 0, []]}

    sets, data = pre_prep(data, sets)
    general_stats = get_general_stats(data)
    set_names = list(sets.keys())

    print()
    print(f"{len(data)} left, runtime {time.time() - start:.2f}")
    while len(data) > 0:
        penalties:List = []

        if len(data)%500==0:
            print(f"{len(data)} left, runtime {time.time() - start:.2f}")

        random.shuffle(data)
        for line in data:
            '''The penalties (p) are orderd training, test, eval'''
            p:list= [0,0,0]
            id, spk_id, sentence = line
            
            for i in range(len(p)):
                p[i] = sentence_cost(sentence, set_names[i], sets)
                p[i] = speaker_cost(spk_id, set_names[i], sets)
                p[i] = set_full_cost(sets[set_names[i]][2], max_value[i])

            lowest_score = get_lowest_score(p)
            penalties.append(get_lowest_score(p))

        index_of_data, penalty, ind_of_set= get_lowest_penalty(penalties)

        #data: id, spk_id, sentece
        #Lets add the speaker id to the set
        sets[set_names[ind_of_set]][0].add(data[index_of_data][1])
        #Lets add the sentence to the set
        sets[set_names[ind_of_set]][1].add(data[index_of_data][2])
        #Lest add to the count in that a given set
        sets[set_names[ind_of_set]][2]+=1
        #Lets add the id of the row in data
        sets[set_names[ind_of_set]][3].append(data[index_of_data][0])

        total_penalty += penalty
        data.remove(data[index_of_data])


    print(general_stats)
    find_overlap(sets, max_value)

    with open('splits_correct.tsv', 'w') as f_out:
        for name in set_names:
            for line in sets[name][3]:
                f_out.write(f"{line}\t{name}\n")             

    end = time.time()
    print(f"Timer: {end - start:.2f}")
    print(f"Total penalty {total_penalty}")

def pre_prep(data:List, sets:Dict):
    '''
    A few speakers contributed alot of sentence.
    Therefor we will handpick the top contributers 
    and add them to the training set
    '''

    spk_ids=[]
    d = defaultdict(int)
    for line in data: 
        spk_ids.append(line[1])
    for w in spk_ids: d[w] += 1 
    d = {k:v for k,v in sorted(d.items(), key=lambda items: items[1], reverse=True)}
    to_remove:set = set()
    cut_line = 10
    for i, line in enumerate(data):
        key, spk_id, sentece = line
        for k in list(d.keys())[0:cut_line]:
            if k == spk_id:
                sets['training'][0].add(spk_id)
                sets['training'][1].add(sentece)
                sets['training'][2]+=1
                sets['training'][3].append((key))
                to_remove.add(i)
    data_replica = data.copy()
    for line in to_remove:
        data.remove(data_replica[line])
        
    plt.plot(list(d.values()))
    mx = max(list(d.values()))
    plt.plot([0]*mx, range(0, mx))
    plt.savefig("distribution.png")
    print(f"Added {len(to_remove)} to the training set")
    return sets, data    

def get_general_stats(data:list):
    '''
    Makes some basic stats to help us verify 
    that this is working.
    data: id, spk_id, sentece
    '''
    output= '\n============STATS===========\n'
    s, spk = [], []
    for line in data:

        spk.append(line[1])
        s.append(line[2])

    output += f"\nThere are {len(set(spk))} unique speakers\n"
    output += "The frequenzy is a follows:\n"
    for k, v in Counter(sorted(Counter(spk).values())).items():
        output += f"{v}\tspekers have {k} occurences\n"

    output += f"\nThere are {len(set(s))} unique sentences\n"
    output += "The frequenzy is a follows:\n"
    for k, v in Counter(sorted(Counter(s).values())).items():
        output += f"{v}\t senteces appear {k} time/s\n"
    output += f""
    
    return output

def find_overlap(sets:Dict, max_value:List):
    """
    To verify that this method works we see how
    much overlap there is between the sets. 
    """
    output = "============OVERLAP STATS===========\n\n"
    set_names=sets.keys()
    for i, key in enumerate(set_names):
        output+=f"There are {len(sets[key][3])} in {key} it should be {max_value[i]}\n"

    #Sentence. Lets find if a sentence is in one or more other sets.
    #Lets first concate all senteces to a set so that there are no
    #duplicates. Then loop through and see how many time we can find 
    #them in the three sets. The dream senario is that they only appear 
    #in one set. 

    all_sentences:set = set()
    for key in set_names:
        all_sentences = all_sentences.union(set(sets[key][1]))

    stats = []
    for line in all_sentences:
        count =0
        for key in set_names:   
            if line in sets[key][1]:
                count += 1
        stats.append(count)

    output+="\nThe overlap of the sentences:\n"
    for k,v in Counter(sorted(stats)).items():
        output+=f"{v}\t sentences appear {k} time/s\n"

    all_speakers:set = set()
    for key in set_names:
        all_speakers = all_speakers.union(set(sets[key][0]))
        
    output+="\nThe overlap of the speakers\n"
    stats = []
    for line in all_speakers:
        count = 0
        for key in set_names:   
            if line in sets[key][0]:
                count += 1
        stats.append(count)

    for k,v in Counter(sorted(stats)).items():
        output+=f"{v}\t speakers appear {k} time/s\n"
    
    stats = {'training': 0, 'test':0, 'both':0}
    for line in sets['eval'][1]:
        add_to =[]
        for key in ['training', 'test']:   
            if line in sets[key][1]:
                add_to.append(key)
        if add_to:
            if len(add_to)==2:
                stats['both']+=1
            else:
                stats[add_to[0]]+=1

    output+="\nEval sentences overlap:\n"
    for k,v in stats.items():
        output+=f"{v}\tsentences in eval appear in {k}\n"

    stats = {'training': 0, 'test':0, 'both':0}
    for line in sets['eval'][0]:
        add_to =[]
        for key in ['training', 'test']:   
            if line in sets[key][0]:
                add_to.append(key)
        if add_to:
            if len(add_to)==2:
                stats['both']+=1
            else:
                stats[add_to[0]]+=1

    output+="\nEval speakers overlap:\n"
    for k,v in stats.items():
        output+=f"{v}\tspeakers in eval appear in {k}\n"

    print(output)

def sentence_cost(sentence:str, set_name:str, sets:dict):
    '''
    Penalty function for sentences. If a given sentence is 
    in the set assigin a penalty. Sentence are in sets['key'][1]
    '''
    tmp_set = exlude_values_in_dict(set_name, sets)
    penalty = 0
    for key in tmp_set.keys():
        if sentence in tmp_set[key][1]:
            if key == 'eval':
                penalty+=1.5
            else:
                penalty+=1
    return penalty

def speaker_cost(spk_id:int, set_name:str, sets:dict):
    """
    Penalty function for speakers. If a given speaker is
    in the set assigin a penalty. Speaker Ids are in set['key][0]
    """
    tmp_set = exlude_values_in_dict(set_name, sets)
    penalty = 0
    for key in tmp_set.keys():
        if spk_id in tmp_set[key][0]:
            if key == 'eval':
                penalty+=2.5
            else:
                penalty+=2
    return penalty

def set_full_cost(count:int, max_value:int):
    """
    If a given set is full we add a high penalty so 
    that the given set will never be choosen.
    """
    if count >= max_value:
        return 1000
    else:
        return 0

def get_lowest_score(p:list):
    """
    We get the lowest score in a given row. If all
    the penalties are the same we return a random 
    set.  When there are many penealties equally low, returns
    a random index amonst them that ar equally low

    First column refers to the penalty and the second 
    is the 0,1,2 for training, test, eval.
    """
    m = min(p)
    ind = random.choice([i for i,j in enumerate(p) if j==m])
    return [p[ind], ind]

def get_lowest_penalty(p:list):
    """
    Find all the occurences of the lowest penalty 
    and choose an random values amongst them.
    returns index-of-chosen-value, penalty-score and index-of-set
    """
    m = min(p)[0]
    ind = [[i, x] for i, x in enumerate(p) if x[0] == m]
    ind = random.choice(ind)
    return ind[0], ind[1][0], ind[1][1]

def exlude_values_in_dict(set:str, sets:Dict):
    '''
    Helper function for the cost funcitons.
    '''
    return {k:v for k,v in sets.items() if k not in [set]}


if __name__ == "__main__":

    path_to_previous_metadata_file = '/data/asr/samromur/samromur_v1/samromur_v1/metadata.tsv'
    precentage_test:int = 10
    precentage_eval:int = 5

    split_data = []
    df = pd.read_csv(path_to_previous_metadata_file, sep='\t', index_col='id')
    for i in tqdm(df.index[0:100000], unit='lines'):
            split_data.append([i, df.at[i, 'speaker_id'], df.at[i, 'sentence_norm']])

    split_train_test_eval(split_data, precentage_test, precentage_eval)
