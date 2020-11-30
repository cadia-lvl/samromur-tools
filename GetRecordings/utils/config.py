import json

with open('./credentials.json') as f:
    credentials = json.load(f)

def get_credentials(cred_type):
    return credentials[cred_type]