

def speaker_mapping(df):
    '''
    Takes in the dataframe and returns a dictionary mapping
    bwtween client_id and speaker id.        
    '''

    speakers:dict = {}
    count: int = 1
    for _, row in df.iterrows():
        if row['client_id'] not in speakers:
            speakers[row['client_id']] = count
            count +=1

    return speakers

def age_mapping(key):
    '''
    Takes in an age value from the format in the database
    and maps it to numerical values

    This needs to be improved for version 2.0
    '''

    age_map:dict = {
        'ungur_unglingur': '13-17',
        'unglingur': '18-19',
        'tvitugt': '20-29',
        'thritugt': '30-39',
        'fertugt': '40-49',
        'fimmtugt': '50-59',
        'sextugt': '60-69',
        'sjotugt': '70-79',
        'attraett': '80-89',
        'niraett': '90'
    } 

    if key in age_map:
        return age_map[key]
    elif not key:
        return 'NAN'
    else:
        return key

def gender_mapping(key):
    '''
    Takes in a string for gender in icelandic and maps it to english 
    '''
    gender_map: dict = {
        'kona': 'female',
        'karl': 'male',
        'annad': 'other' 
    }

    if key in gender_map:
        return gender_map[key]
    elif not key:
        return 'NAN'
    else:
        return key


def nationality_mapping(key):
    '''
    Takes in a string for speakers language in icelandic and maps it to english 
    '''
    nationality_map: dict = {
        'albanska': 'Albanian',
        'arabiska': 'Arabic',
        'bulgarska': 'Bulgarian',
        'danska': 'Danish',
        'eistneska': 'Estonian',
        'enska': 'English',
        'faereyska': 'Faroese',
        'filippseyskt_mal': 'Filipino',
        'finnska': 'Finnish',
        'franska': 'French',
        'graenlenska': 'Greenlandic',
        'griska': 'Greek',
        'hebreska': 'Hebrew',
        'hindi': 'Hindi',
        'hollenska': 'Dutch',
        'indonesiska': 'Indonesia',
        'islenska': 'Icelandic',
        'italska': 'Italian',
        'japanska': 'Japanese',
        'kinverska': 'Chinese',
        'koreska': 'Korean',
        'kurdiska': 'Kurdish',
        'lettneska': 'Latvian',
        'litaiska': 'Lithuanian',
        'makedonska': 'Macedonian',
        'mongolska': 'Mongolian',
        'nepalska': 'Nepali',
        'norska': 'Norwegian',
        'persneska': 'Persian',
        'polska': 'Polish',
        'portugalska': 'Portuguese',
        'rumenska': 'Romania',
        'russneska': 'Russia',
        'saenska': 'Swedish',
        'serbokroatiska': 'Serbo-Croatian',
        'singhalesiska': 'Sinhala',
        'slovakiska': 'Slovak',
        'slovenska': 'Slovenian',
        'spaenska': 'Spanish',
        'svahili': 'Swahili',
        'tailenska': 'Thai',
        'tamil': 'Tamil',
        'tekkneska': 'Czech',
        'thyska': 'German',
        'tyrkneska': 'Turkish',
        'ukrainska': 'Ukrainian',
        'ungverska': 'Hungarian',
        'urdu': 'Urdu',
        'vietnamska': 'Vietnamese',
        'annad': 'other',

    }

    if key in nationality_map:
        return nationality_map[key]
    elif not key:
        return 'NAN'
    else:
        return key

def dialect_mapping(key):
    the_map: dict = {
        "0":'Harðmæli',
        "1":'Raddaður framburður',
        "2":'ngl-framburður',
        "3":'bð/gð-framburður',
        "4":'Vestfirskur einhljóðaframburður' ,
        "5":'Vestfirsk áhersla',
        "6":'hv-framburður',
        "7":'Skaftfellskur einhljóðaframburður',
        "8":'rn/rl-framburður'}    
        
    if key in the_map:
        return the_map[key]
    elif not key:
        return 'NAN'
    else:
        return key