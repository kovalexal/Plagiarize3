import multiprocessing
import subprocess
import os

from download import download
import google
from hash import md5sum_file, md5sum_str
#from split import get_list
from keywords import generateCandidateKeywords
import shingles

class file:
    def __init__(self, url = "", path_pdf = "", path_txt = path_pdf + ".txt"):
        self.url = url
        self.path_pdf = path_pdf
        self.path_txt = path_txt
        if (self.path_pdf == ''):
            self.hash = ""
            self.size = 0
        else:
            self.hash = md5sum_file(path_pdf)
            self.size = os.path.getsize(self.path_pdf)
        #If processed = 0, then it has not yet been processed, 1 - successfully processed
        #-1 - cannot be processed
        self.processed = 0
        self.words = []
        self.shingles = []

    def __eq__(self, compfile):
        return self.hash == compfile.hash
        
f = open("output", "r")
keyphrases = f.readlines()
f.close()
#Just an example hash
#input_file_hash = "c52ddbefea727246a1566f669974b144"
input_file_hash = "d41d8cd98f00b204e9800998ecf8427e"
input_text = ""
stopwords = set()
lemmatizer = None

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
        print("\nStarted parsing PDF \"{0}\"".format(f.path_pdf))
        try:
            retcode = subprocess.call(["python", "./pdf_import.py", f.path_pdf, f.path_txt])
            if (retcode != 0):
                print("Error while parsing {0}".format(f.path_pdf))
            else:
                print("\nSuccessfully ended parsing \"{0}\"".format(f.path_pdf))
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
print("\nGetting shingles for txt files")
for f in files:
    if (f.processed == 1):
        words = []
        f_tmp = open(f.path_txt,"r")
        text = f_tmp.read()
        f_tmp.close()
        candidate_keywords = generateCandidateKeywords(text, stopwords, lemmatizer)
        for sublist in candidate_keywords:
            for word in sublist:
                words.append(word)
        f.words = words
        f.shingles = shingles.gen_shingles(words)
        if (len(f.shingles) == 0):
            print("\nNo shingles were built in file \"{0}\"\nPossible, a file is empty - PDF parse error\n".format(f.path_txt))
            f.processed = -1


"""
Work with input file
"""
print("Started work with main file")
input_file_path = "./Task/Выделение набора ключевых слов/0470749822.pdf"
input_file = file(path = input_file_path)
try:
    retcode = subprocess.call(["python", "./pdf_import.py", f.path_pdf, f.path_txt])
    if (retcode != 0):
        print("Error while parsing {0}".format(f.path_pdf))
        exit(-1)
except:
    print("Error while parsing {0}".format(f.path_pdf))
    exit(-1)
input_file.processed = 1
words = []
f_tmp = open(input_file.path_txt, "r")
input_text = f_tmp.read()
f_tmp.close()
candidate_keywords = []
candidate_keywords = generateCandidateKeywords(input_text, stopwords, lemmatizer)
for sublist in candidate_keywords:
    for word in sublist:
        words.append(word)
input_file.words = words
input_file.shingles = shingles.gen_shingles(words)
print(len(input_file.shingles))

number = 0
for f in files:
    number += 1
    if (f.processed == 1):
        print("{0}) {1}".format(number, shingles.compare(input_file.shingles, f.shingles)))

