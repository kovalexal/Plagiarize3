import hashlib

def md5sum(path):
    '''
    Generating md5 for a file
    '''
    md5 = hashlib.md5()
    with open(path,'rb') as f: 
        for chunk in iter(lambda: f.read(8192), b''): 
            md5.update(chunk)
    return md5.hexdigest()