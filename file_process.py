import threading
import subprocess
import re
from time import time
import os
from threading import Thread, Lock

from hash import md5sum_file
from keywords import generateCandidateKeywords
from config import *
import download
import shingles

class file:
    def __init__(self, url = "", path = None, path_txt = None):
        self.url = url
        self.path = path
        if (path_txt != None):
            self.path_txt = path_txt
        else:
            if (path != None):
                self.path_txt = path + ".txt"
            else:
                self.path_txt = None
        self.text = ""
        self.hash = ""
        self.words = []
        #self.shingles = []
        self.appropriate = True
        self.similarity = -1

    def makehash(self):
        if (self.path != None):
            self.hash = md5sum_file(self.path)
        else:
            self.hash = ""

def parse_pdf(f):
    '''
    Function for PDF processing to TXT
    '''
    retcode = 0
    if (f.appropriate == True):
        if (f.path == None):
            return retcode
        threadLock.acquire()
        print("Started parsing \"{0}\"".format(f.path), end = "\n\n")
        threadLock.release()
        str_run = "python ./pdf_import.py {0} {1}".format(f.path, f.path_txt)
        try:
            retcode = subprocess.call(str_run.split())
        except:
            threadLock.acquire()
            print("Error during processing \"{0}\"".format(f.path), end = "\n\n")
            f.appropriate = False
            threadLock.release()
            #return -1
        if (retcode != 0):
            threadLock.acquire()
            print("Error during processing \"{0}\"".format(f.path), end = "\n\n")
            f.appropriate = False
            threadLock.release()
            #return -1
        else:
            threadLock.acquire()
            print("Successfully ended processing \"{0}\"".format(f.path), end = "\n\n")
            threadLock.release()
    return retcode

def cast_string(string):
    '''
    Replaces non-printable symbols with ""
    '''
    rx = re.compile(NON_PRINTABLE_SYMBOLS)
    return re.sub(rx, "", string)

def get_text(f):
    '''
    Gets text from a txt file f
    '''
    if (f.path_txt != None):
        tmp_file = open(f.path_txt, "r")
        string = tmp_file.read()
        string = cast_string(string)
        tmp_file.close()
        return string
    return ""

def get_words(f, stopwords = set(), lemmatize = None):
    '''
    Generate shingles for a file f
    '''
    words = []
    candidate_keywords = generateCandidateKeywords(f.text, stopwords, lemmatizer = lemmatize)
    for phrases in candidate_keywords:
        for word in phrases:
            words.append(word)
    return words

#Mutex for synchronizing threads
threadLock = Lock()

class file_process_thread(Thread):
    def __init__(self, threadID, url, stopwords = set(), compare_file = None, group=None, target=None, name=None, args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
        self._id = threadID
        self._file = file(url = url)
        self._compare_file = compare_file
        self._stopwords = stopwords
    def run(self):
        """
        Downloading files
        """
        try:
            threadLock.acquire()
            print("{0}) Downloading \"{1}\"".format(self._id, self._file.url), end = "\n\n")
            threadLock.release()
            self._file.path = download.download(self._file.url, directory = DOWNLOAD_DIR, callback = None)
            if (self._file.path == ""):
                threadLock.acquire()
                print("Error, during downloading (server is not corresponding)")
                print("\"{0}\"".format(self._file.url), end = "\n\n")
                threadLock.release()
                self._file.appropriate = False
                self._return = None
                return
        except:
            threadLock.acquire()
            print("Download \"{0}\" failed".format(self._file.url), end = "\n\n")
            threadLock.release()
            exit(0)
        else:
            threadLock.acquire()
            print("File \"{0}\"".format(self._file.url))
            print("Saved in \'{0}\'".format(self._file.path), end = "\n\n")
            threadLock.release()

        """
        Checking hash sum for coinsidence
        """
        self._file.makehash()
        if (self._file.hash == self._compare_file.hash):
            self._file.similarity = "HASH_COINSIDENCE"
            self._return = self._file
            '''
            You can delete it
            '''
            threadLock.acquire()
            print('////////////////////////////////////////////')
            print("Similarity with file")
            print("\'{0}\'".format(self._file.url))
            print("is")
            print("HASH_COINSIDENCE")
            print('////////////////////////////////////////////', end = "\n\n")
            threadLock.release()
            return

        """
        Parsing PDFs into TXTs
        """
        self._file.path_txt = self._file.path + ".txt"
        threadLock.acquire()
        start_time = time()
        print("Started parsing \"{0}\"".format(self._file.path), end = "\n\n")
        threadLock.release()
        parse_result = parse_pdf(self._file)
        end_time = time()
        threadLock.acquire()
        print("Parsing \"{0}\" took {1:.3f}".format(self._file.path, end_time - start_time), end = "\n\n")
        threadLock.release()
        if (self._file.appropriate == False):
            self._return = None
            return

        threadLock.acquire()
        print("Started getting shingles for file \"{0}\"".format(self._file.path_txt), end = "\n\n")
        threadLock.release()

        start_time = time()
        self._file.text = get_text(self._file)
        self._file.words = get_words(self._file, self._stopwords)
        self._file.shingles = shingles.gen_shingles(self._file.words)
        end_time = time()
        if len(self._file.shingles) == 0:
            threadLock.acquire()
            print("No shingles were built in file \"{0}\"".format(self._file.path_txt), end = "\n\n")
            threadLock.release()
            self._return = None
            return
           
        threadLock.acquire() 
        print("Shingles were built successfully for an file \"{0}\"".format(self._file.path_txt))
        print("Took about {0:.3f}s".format(end_time - start_time), end = "\n\n")
        threadLock.release()

        """
        Comparing, files, using shingles
        """
        threadLock.acquire()
        print("Started getting similarity based on shingles in file \"{0}\"".format(self._file.path_txt), end = "\n\n")
        threadLock.release()
        start_time = time()
        self._file.similarity = shingles.compare(self._compare_file.shingles, self._file.shingles)
        end_time = time()
        threadLock.acquire()
        print("Ended comparing shingles for file \"{0}\"".format(self._file.path_txt))
        print("Took {0:.3f}s".format(end_time - start_time), end = "\n\n")
        threadLock.release()

        threadLock.acquire()
        print('////////////////////////////////////////////')
        print("Similarity with file")
        print("\'{0}\'".format(self._file.url))
        print("is")
        print("{0:.3f}".format(self._file.similarity))
        print('////////////////////////////////////////////', end = "\n\n")
        threadLock.release()

        self._return = self._file

    def join(self):
        Thread.join(self)
        #print(self._return)
        return self._return


dictionary = {}
current_number = 0

def enumerate_words(list_):
    '''
    Enumerates words and return a list of numbers
    '''
    global dictionary, current_number
    result_list = []
    for word in list_:
        try:
            value = dictionary[word]
        except KeyError:
            value = current_number
            dictionary[word] = value
            current_number += 1
        result_list.append(value)
    return result_list


if __name__ == "__main__":
    threadLock = Lock()
    threads = []

    url1 = "www.google.com"
    url2 = "www.yandex.ru"

    #thread1 = file_process_thread(1, url1)
    #thread2 = file_process_thread(2, url2)

    thread1 = file_process_thread(1, "http://www.gov.pe.ca/law/statutes/pdf/d-13.pdf")
    thread2 = file_process_thread(2, "http://www.leeparks.org/pdf/Dog-friendly-facilities-for-web.pdf")

    thread1.start()
    thread2.start()

    threads.append(thread1)
    threads.append(thread2)

    for t in threads:
        return_value = t.join
        #return_value = return_value()
        #print(return_value)