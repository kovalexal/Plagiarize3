import multiprocessing
import subprocess
import os

from download import download
import google
from hash import md5sum_file, md5sum_str
from split import get_list

class file:
    def __init__(self, url = "", path = ""):
        self.url = url
        self.path_pdf = path
        self.path_txt = path + ".txt"
        if (self.path_pdf == ''):
            self.hash = ""
            self.size = 0
        else:
            self.hash = md5sum_file(path)
            self.size = os.path.getsize(self.path_pdf)
        #If processed = 0, then it has not yet been processed, 1 - successfully processed
        #-1 - cannot be processed
        self.processed = 0
        self.words = []

    def __eq__(self, compfile):
        return self.hash == compfile.hash
        
f = open("output")
keyphrases = f.readlines()
f.close()
#Just an example hash
#input_file_hash = "c52ddbefea727246a1566f669974b144"
input_file_hash = "d41d8cd98f00b204e9800998ecf8427e"
input_text_words = []

query = ''
for tmp in keyphrases:
    query += "+(" + tmp[:-1] + ")"

urls = google.find(query, filetype = "pdf")

files = []
number = 0
for url in urls:
    try:
        number += 1
        print("\n{0})".format(number), end = "")
        path = download(url, directory = "./TMP")
        f = file(url, path)
        if (path == ''):
            f.processed = -1
        files.append(f)
    except:
        print("Download\n\"{0}\"\nfailed\n".format(url))
        f.processed = -1

def process(f):
    '''
    Function, which will create a new process, which get a txt from pdf
    '''
    retcode = 0
    if (f.processed == 0):
        print("\n\nStarted parsing {0}".format(f.path_pdf))
        try:
            retcode = subprocess.call(["python", "./pdf_import.py", f.path_pdf, f.path_txt])
            if (retcode != 0):
                print("Error while parsing {0}".format(f.path_pdf))
            return retcode
        except:
            print("Error while parsing {0}".format(f.path_pdf))
            return retcode


'''
Starting processing pdf to txt
'''
count = multiprocessing.cpu_count()
pool = multiprocessing.Pool(processes=count)
return_codes = pool.map(process, files)
for i in range(len(return_codes)):
    if (return_codes[i] == 0):
        files[i].processed = 1
    else:
        files[i].processed = -1

'''
Checking hash sums for coincidence
'''
for f in files:
    if (input_file_hash == f.hash):
        print("\nPlagiarize: {0}\nin file: \"{1}\"\ndownloaded from: \"{2}\"".format(1.0, f.path_pdf, f.url))

'''
Started getting words from txts
'''
print("Started parsing txt files")
for f in files:
    if f.processed == 1:
        f.words = [(word, md5sum_str(word)) for word in get_list(f.path_txt, enableComments = False, sorted = False, lowerCase = True)]

