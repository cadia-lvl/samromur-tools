import os
import time
from xml.etree import ElementTree as ET
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
import json

from util.normalization import (clean_text_from_xml)
from util.filters import (filter_allowed_letters_and_symbals, filter_right_length, 
filter_only_words_in_BIN, filter_out_sentences_with_bad_words, filter_max_character_count)


class Timer():
    '''
    Timer class for exicution time results.
    '''
    def __init__(self):
        self.startTime = time.time()
    
    def showTimer(self):
        runtime = round((time.time()-self.startTime)/60, 2)
        return(f'\nRuntime: {runtime} min\n')

class TextParser():
    def __init__(self, args):
        if args.code_name:
            self.codes: str = args.code_name
        else:
            self.codes: str = ''
        self.codes: list = []
        self.number_of_jobs:int = args.n_jobs
        self.output_directory: str = args.output_folder
        self.file_extensions: str = args.file_type
        self.current_directory: str = ''
        self.set_origin: str = None

        if args.process_rmh:
            self.current_directory = args.process_rmh
        elif args.process_text:
            self.current_directory = args.process_text
            self.set_origin = args.code_name
        else:
            print('Input missing program will crash')
        
        self.s_min = args.s_min
        self.s_max = args.s_max
        self.word_max = args.w_max
        
        #skítamix hér sem ég geri aftur í filters.py, laga við tækifæri
        with open('configs/conf.json', 'w') as f_out: 
            json.dump({'sentence_max': self.s_max, 'sentence_min': self.s_min, 'word_max':self.word_max}, f_out)

    def create_directory(self):
        os.makedirs(self.output_directory, exist_ok=True)

    def get_file_lenght(self):
        line_count:int = 0
        with open(self.current_directory, 'r') as f_in:
            for line in f_in:
                line_count += 1
        return line_count

    def get_file_directories(self):
        print(f'Getting list of files form {self.current_directory} and its subfolders')
        filepath_list: list = []
        for dirName, _subdirList, fileList in os.walk(self.current_directory, topdown=False):
            for fname in fileList:
                filepath_list.append(dirName + '/' + fname)  
        
        print(f'Done, found {len(filepath_list)} files')
        return filepath_list

    def update_current_directory_and_codes(self, new_code):
        if self.codes:
            self.current_directory = self.output_directory + '/'
            self.codes.append(new_code)
            if_first = True
            for c in self.codes:
                if if_first:
                    self.current_directory += c
                    if_first = False
                else:
                    self.current_directory += '_' + c
            self.current_directory += self.file_extensions 
        else:
            self.current_directory = self.output_directory + '/' + new_code + self.file_extensions
            self.codes = [new_code] 

    def open_file_add_to_set(self):
        text: set = set()
        with open(self.current_directory, 'r') as f_in:
            for line in f_in:
                if self.set_origin:
                    text.add(line+'\t'+self.set_origin)
                else:
                    text.add(line)
        if self.set_origin:
            self.set_origin = None
        return text

    def parallel_processor(self, function, iterator, write_mode='line',chunks=100, units ='files'):
        results: set = set()
        with open(self.current_directory, 'w+', encoding='utf-8') as f_out:
            with ProcessPoolExecutor(max_workers=self.number_of_jobs) as executor:
                results =  tqdm(executor.map(
                    function,
                    iterator,
                    chunksize=chunks), 
                    total=len(iterator),
                    unit= ' '+ units)
                for chunk in results:
                    if chunk:
                        if write_mode == 'list':
                            f_out.writelines(chunk)             
                        elif write_mode == 'line':
                            f_out.write(chunk)             
                        else:
                            print('Unspecified write method, please fix')

    def read_file(self, path: str): 
        NS = {'a': 'http://www.tei-c.org/ns/1.0'}
        root = ET.parse(path).getroot()
        origin: str = root.find('.//a:monogr', NS)[0].text
        origin = origin.replace(' ','_')
        text: set = set()
        for seg in root.findall('.//a:s', NS): 
            sentence: list = []
            for node in seg.getchildren():
                sentence.append(node.text)           
            text.add(' '.join(sentence)+'\t'+origin+'\n')
        return text

    def read_corpus(self):
        print('Reading the corpus')
        code: str = 'rmh'
        paths: list = self.get_file_directories()
        self.update_current_directory_and_codes(code) 
        self.parallel_processor(self.read_file,paths,write_mode='list')
        
    def normalize_text(self):
        print('Normalizing the text')
        code: str = 'normalized'
        text: set = self.open_file_add_to_set()
        self.update_current_directory_and_codes(code) 
        self.parallel_processor(clean_text_from_xml, text, write_mode='list')

    def allowed_symbals(self):
        print('Checking allowed symbals')
        code: str = 'OK_symbals'
        text: set = self.open_file_add_to_set()
        self.update_current_directory_and_codes(code) 
        self.parallel_processor(clean_text_from_xml, text, write_mode='list')

    def right_length(self):
        print(f'Finding all sentences that are between {self.s_min} and {self.s_max} word long')
        code: str = f'{self.s_min}_{self.s_max}'
        text: set = self.open_file_add_to_set()
        self.update_current_directory_and_codes(code) 
        self.parallel_processor(filter_right_length, text, write_mode='list')

    def only_words_in_BIN(self):
        print('Filtering out words that arent in BÍN')
        code: str = 'BIN'
        text: set = self.open_file_add_to_set()
        self.update_current_directory_and_codes(code) 
        self.parallel_processor(filter_only_words_in_BIN, text, write_mode='list')

    def remove_sentences_with_bad_words(self):
        print('Filtering out bad words')
        code: str = 'kid_friendly'
        text: set = self.open_file_add_to_set()
        self.update_current_directory_and_codes(code) 
        self.parallel_processor(filter_out_sentences_with_bad_words, text, write_mode='list')   

    def right_length_of_word(self):
        print(f'Finding all sentences that only have words shorter then {self.word_max}')
        code: str = f'{self.word_max}'
        text: set = self.open_file_add_to_set()
        self.update_current_directory_and_codes(code) 
        self.parallel_processor(filter_max_character_count, text, write_mode='list')