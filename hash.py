import hashlib

def md5sum_file(path):
    '''
    Generating md5 for a file
    '''
    md5 = hashlib.md5()
    with open(path,'rb') as f: 
        for chunk in iter(lambda: f.read(128*md5.block_size), b''): 
            md5.update(chunk)
    return md5.hexdigest()

def md5sum_str(str):
    '''
    Generating md5sum for a string
    '''
    md5 = hashlib.md5()
    md5.update(str.encode("utf-8"))
    return md5.hexdigest()