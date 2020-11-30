from util.argparser import create_parser
from util.modules import (Timer, TextParser)


def main():
    #Initilize timer class
    timer = Timer()

    #Initilize parser class
    parser = TextParser(args)
    
    parser.create_directory()

    parser.read_corpus()
        
    parser.normalize_text()

    parser.allowed_symbals()

    parser.right_length()

    parser.only_words_in_BIN()

    parser.remove_sentences_with_bad_words()
    
    parser.right_length_of_word()
    
    print(f'\nFound {parser.get_file_lenght()} sentences')
    print(timer.showTimer())
    print('Finished task')

if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()

    main()