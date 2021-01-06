import json, os
root = os.getcwd()
root = root.replace('util', '')

#Breyta þessu í klasa!
'''
class Filter_modules:
    def __init__(self):
'''        

#Load config file 
conf:dict = {}
with open(root+'/configs/conf.json', 'r') as in_file: 
    conf = json.load(in_file)

#Symbols and characters that we allow in the scripts
allowed_symbols = set([line.rstrip() for line in open(root+'/configs/allowed_symbols.txt')])
allowed_symbols.add(' ') #Fix þar sem ég við viljum alltaf hafa bil.
allowed_letters = set([line.rstrip() for line in open(root+'/configs/allowed_letters.txt')])

#Decalre an empty set for BIN
BIN = set([line.strip().lower() for line in open(root+'/data/ordmyndir.txt')])

#Decalre an empty set for bad words
bad_words = set([line.rstrip() for line in open(root+'/data/bad_words.txt')])

#Decalare these global variables
max_length: int = conf['sentence_max']
min_length: int = conf['sentence_min']

def filter_allowed_letters_and_symbals(s:str):
    '''
    This filter returns false if sentece s includes disallowd characters or symbles
    '''
    #if the orgin tag is also in the string
    s, origin = s.split('\t')

    allowed_symbols_and_letters = allowed_symbols | allowed_letters
    
    only_allowed_letters = True
    s = s.rstrip()
    for l in s: 
        if l not in allowed_symbols_and_letters:
            only_allowed_letters = False 
            break
    
    if only_allowed_letters:
        return s +'\t'+ origin
    else:
        return None

def filter_right_length(s:str):
    '''
        Return true if sentece is within the boundery of sentence max and min length
    '''
    s, origin = s.split('\t')
    s = s.rstrip()
    length = len(s.split(' '))
    if length >= min_length and length <= max_length:
        return s +'\t'+ origin
    else:
        return None

def filter_only_words_in_BIN(s: str):
    '''
    This filter returns false if sentece has a word that isin't BIN
    '''
    #if the orgin tag is also in the string
    s, origin = s.split('\t') 
    
    s_simple = s
    for symbol in allowed_symbols:
        if symbol in s_simple:
            s_simple = s_simple.replace(symbol, ' ')

    for word in s_simple.split():
        word = word.lower()
        if word not in BIN:
            #print('found word: ', word,'\t', s) #Það getur verið áhugavert að skoða þetta
            return None  

    return s +'\t'+ origin

def filter_out_sentences_with_bad_words(s: str):
    '''
    This filter returns false if sentece has a bad word in it.
    '''
    #if the orgin tag is also in the string

    s, origin = s.split('\t') 
    
    s_simple = s
    for symbol in allowed_symbols:
        if symbol in s_simple:
            s_simple = s_simple.replace(symbol, ' ')

    for word in s_simple.split():
        word = word.lower()
        if word in bad_words:
            #print('found word: ', word, s)  #Það getur verið áhugavert að skoða þetta
            return None  

    return s +'\t'+ origin

def filter_max_character_count(s:str):
    '''
        Return none if the words in the sentence are within the boundery
    '''
    s, origin = s.split('\t')

    sentence = s.split(' ')
    for word in sentence:
        if len(word) >= conf['word_max']:
            return None
    return s +'\t'+ origin
