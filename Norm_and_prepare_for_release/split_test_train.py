import random
from tqdm import tqdm

def split_train_test_eval(text, percentage_test, percentage_eval): 
    """ 
    Given a file that contains <id's>\t<sentence> 
    Returns a dict <id: "test"/"traning"> given a 
    split preventage. The input text is shuffled 
    and no overlap of sentence is in the test and
    training set. 
    """
    
    random.shuffle(text)
    status:dict = {}
    test_senteces = set()
    eval_senteces = set()

    test_size = int(len(text)*(percentage_test/100))
    eval_size = int(len(text)*(percentage_eval/100))
    training_size = len(text) - test_size - eval_size

    print(f"\nThe total text is {len(text)} lines")
    print(f"The training_size set is {training_size} lines")
    print(f"The test set is {test_size} lines")
    print(f"The eval set is {eval_size} lines\n")


    test_count, eval_count = 0,0 

    for line in tqdm(text):
        key, sentece = line
        if sentece not in test_senteces and test_count < test_size:
            test_senteces.add(sentece)
            status[key] = 'test'
            test_count +=1
        elif sentece not in test_senteces and sentece not in eval_senteces and eval_count < eval_size:
            eval_senteces.add(sentece)
            status[key] = 'eval'
            eval_count += 1
        else:
            status[key] = 'training'


    assert test_count == test_size or eval_size == eval_count,\
        print(f"Eval or test size is not as expected\nTest: {test_count} {test_size}\nEval: {eval_size} {eval_count}")

    return status
