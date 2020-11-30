import re

def pick_apart_goose(s):
    #Auðvita þýðast gæsalappir sem goose. 
    first = True
    w = ''
    for letter in s:
        if letter == '"' and first:
            w = w + (' „')
            first = False
        elif letter == '"' and not first:
            w = w + ('“ ')
            first = True
        else:
            w = w + letter
    return w

def hyphen_between_numbers(s): 
    #Fix space between hyphen of numbers.
    #Ex. 1994 - 1995 will be 1994-1995.
    if re.search(r'[0-9]+\s*-\s*[0-9]+', s):
            s = re.sub(r'\s\-\s', '-', s)
    return s    

def clean_text_from_xml(s: str):
    #if the orgin tag is also in the string
    s, origin = s.split('\t')
    #s = re.sub(rr'\n', ' ', s)

    #Tek burt bil í upphafi og enda setningar
    s = re.sub(r'^\s', '', s)
    s = re.sub(r'\s$', '', s)

    #Set allar gæsalappir sem enskar gæsalappir og
    #skipiti þeim síðan út fyrir íslenskra. Virkar 90%.
    s = re.sub(r'[\„|\“|\"]', '"', s)
    if re.search('.*".*"', s):
        s = pick_apart_goose(s)
    s = re.sub(r'\„\s', '„', s)
    s = re.sub(r'\s\“', '“', s)
    s = re.sub(r'\.\“', '“', s)
    s = re.sub(r'\,\“', '“', s)
    s = re.sub(r'"', '', s)  #Kærum okkur ekkert um aðrar gæsalappir
    s = re.sub(r'[„|“]', '', s) # Þetta mætti endurskoða en við það að skoða nokkrar skrár þá eru gæsalappir tilgangslausar

    #Ef það eru fleiri en ein setnig í línu.
    s = re.sub(r'\s\.\s', '.\n', s)
    s = re.sub(r'\s\?\s', '?\n', s)
    s = re.sub(r'\s\!\s', '!\n', s)

    #Laga bandstrik
    #s = hyphen_between_numbers(s)
    s = re.sub(r'\s\-', '-', s)

    #Tek burtu bil í kringum sviga, hornklofa og önnur tákn
    s = re.sub(r'\(\s', '(', s)
    s = re.sub(r'\s\)', ')', s)
    s = re.sub(r'\s\/\s', '/', s)
    s = re.sub(r'\[\s', '[', s)
    s = re.sub(r'\s\]', ']', s)
    
    #Tek burtu bil á undan punkti og öðrum táknum
    s = re.sub(r'\s\.', '.', s)
    s = re.sub(r'\'\s|\s\´', '\'', s)
    s = re.sub(r'\s\$ ', '$', s)
    s = re.sub(r'\s\?', '?', s)
    s = re.sub(r'\s\%', '%', s)
    s = re.sub(r'\s\!', '!', s)
    s = re.sub(r'\s\:', ':', s)
    s = re.sub(r'\s,', ',', s)
    s = re.sub(r'\s\;', ';', s)
    s = re.sub(r'\s\*', '*', s)
    s = re.sub(r'\s\@', '@', s)
    s = re.sub(r'\“\s\.', '“.', s)

    #Tek burtu tákn
    s = re.sub(r'\'\'', '', s)
    s = re.sub(r'\‘', '\'', s)
    s = re.sub(r'\,\,', '', s)
    s = re.sub(r'\.{2,}', '.', s)
    s = re.sub(r'\-{2,}', ' ', s)
    s = re.sub(r'\.\?','?', s)

    #Tek burtu tákn sem birstast of í upphafi setningar
    s = re.sub(r'^\s*', '', s)
    s = re.sub(r'^[\:|\-| \"\s|\,]*', '', s)
    s = re.sub(r'^\s*', '', s)

    #Tek burtu auk bil ef það eru tvö eða fleiri
    s = re.sub(r'\s{2,}', ' ', s)

    #Tek burtu newline ef það eru einhver
    s = re.sub(r'\n', '', s)

    return s + '\t'+ origin

def remove_brackets(s):
    #Remove everything within parentheses or brackets    
    s = re.sub(r'([\(\[\<]).*?([\)\]\>])', '', s)
    s = re.sub(r'\s{2,}', ' ', s)
    s = re.sub(r'\n{2,}', '\n', s)
    return s