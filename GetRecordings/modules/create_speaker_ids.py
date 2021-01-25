'''
Function to create the speaker-ids
This function will not be needed oance this is integraded to web soon.
'''

def create_speaker_ids(df):
    '''
    Takes in the dataframe and returns a dictionary mapping for speaker ids.        
    '''

    spks:dict = {}
    id =1
    for i in df.index:
        combination = f"{df.at[i, 'client_id']}/{df.at[i, 'age']}/{df.at[i, 'gender']}/{df.at[i, 'native_language']}"	
        if combination not in spks.keys():
            spks[combination] = str(id).zfill(6)
            id += 1

    speaker_ids:list=[]
    for i in df.index:
        combination = f"{df.at[i, 'client_id']}/{df.at[i, 'age']}/{df.at[i, 'gender']}/{df.at[i, 'native_language']}"	
        speaker_ids.append(spks[combination])

    return speaker_ids
