import multiprocessing
import subprocess
import os

from download import download
import google
from hash import md5sum

class file:
    def __init__(self, url = "", path = ""):
        self.url = url
        self.path = path
        if (self.path == ''):
            self.hash = "d41d8cd98f00b204e9800998ecf8427e"
            self.size = 0
        else:
            self.hash = md5sum(path)
            self.size = os.path.getsize(self.path)
        self.processed = 0
        #If processed = 0, then it has not yet been processed, 1 - successfully processed
        #-1 = failure during processing

    def __eq__(self, compfile):
        return self.hash == compfile.hash
        
f = open("output")
keyphrases = f.readlines()
f.close()
input_file_hash = "c52ddbefea727246a1566f669974b144"

query = ''
for tmp in keyphrases:
    query += "+(" + tmp[:-1] + ")"

urls = google.find(query, filetype = "pdf")

#for url in urls:
    #print(url)

files = []
for url in urls:
    try:
        path = download(url, directory = "./TMP")
        if (path == ''):
            f.processed = -1
        f = file(url, path)
        f.processed = 0
        files.append(f)
    except:
        print("Download\n{0}\nfailed\n".format(url))
        f.processed = -1

#run = [("python ./pdf_import.py" + f.path, f.path) for f in files]
#print(run)

def process(f):
    if (f.processed == 0):
        print("\n\nStarted parsing {0}".format(f.path))
        retcode = subprocess.call(["python", "./pdf_import.py", f.path, f.path + ".txt"])
        if retcode != 0:
            print("\nParsing \"{0}\" failed".format(f.path))

files[2].processed = -1

if __name__ == '__main__':
    count = multiprocessing.cpu_count()
    #print(count)
    pool = multiprocessing.Pool(processes=count)
    pool.map(process, files)
    #print(pool.map(work, ['ls'] * count))