import os
import sys
import argparse
import subprocess
import multiprocessing
from time import time
import colorama
from colorama import Fore, Back, Style

import split
import stem
import keywords
import google
from download import download
from hash import md5sum_file, md5sum_str
from keywords import generateCandidateKeywords
import shingles
from config import *

def colour_print(text, colour = Fore.WHITE, back = Back.BLACK):
    '''
    Console color output
    colour -> font colout
    back -> background color
    '''
    print(colour + back + str(text) + Style.RESET_ALL)

def parsePDF(f):
    '''
    Function for parallelizing PDF processing
    '''
    retcode = 0
    if (f.processed == 0):
        print("Started parsing \"{0}\"".format(f.path_pdf), end = "\n\n")
        #try:
        #retcode = subprocess.call("python", "./pdf_import.py", f.path_pdf, f.path_txt)
        str_run = "python ./pdf_import.py {0} {1}".format(f.path_pdf, f.path_txt)
        #str_run = "python ./pdf_import.py" + "\""f.path_pdf  + " " f.path_txt
        retcode = subprocess.call(str_run.split())
        if (retcode != 0):
            print("Error during processing \"{0}\"".format(f.path_pdf), end = "\n\n")
        else:
            print("Successfully ended processing \"{0}\"".format(f.path_pdf), end = "\n\n")
        return retcode
        #except:
            #print("Error during processing \"{0}\"".format(f.path_pdf))
            #return retcode
    else:
        return retcode

def shingles_file(f):
    '''
    Function for getting shingles for a file f
    '''
    print("Started getting shingles for file \"{0}\"".format(f.path_txt))
    start_time = time.time()
    if (f.processed == 1):
            f_tmp = open(f.path_txt, "r")
            f.text = f_tmp.read()
            f_tmp.close()
            candidate_keywords = generateCandidateKeywords(f.text, stopwords, lemmatizer = lemmatizer.get())
            for phrases in candidate_keywords:
                for word in phrases:
                    f.words.append(word)
            f.shingles = shingles.gen_shingles(f.words)
            if (len(f.shingles) == 0):
                print("No shingles were built in \"{0}\"".format(f.path_txt))
                f.processed = -1
                return
    end_time = time.time()
    print("Getting shingles for file \"{0}\"\ntook {1:.3f}".format(f.path_txt, end_time - start_time))
    

class lemmatize:
    languages = set({"ru", "en"})
    def __init__(self, lang = None):
        self.lang = lang
    def get(self):
        if (self.lang == "ru"):
            return stem.lemmatize_ru
        elif (self.lang == "en"):
            return stem.lemmatize_en
        else:
            return None


class file:
    def __init__(self, url = None, path_pdf = None, path_txt = None, keywords = None):
        self.url = url
        self.path_pdf = path_pdf
        self.path_txt = path_txt
        if (path_pdf != None):
            self.path_txt = path_pdf + ".txt"
        self.words = []
        self.text = ""
        self.keywords = keywords
        self.shingles = []
        '''
        If processed == -1, then no error appeared, during work with file
        if processed == 0, then file has not yet been processed
        if processed == 1, then file was successfully processed
        '''
        self.processed = 0

    def hash(self):
        self.size = os.path.getsize(self.path_pdf)
        
        if (self.path_pdf != ''):
            self.hash = md5sum_file(self.path_pdf)
        else:
            self.hash = ""

if __name__ == "__main__":
    EXTRA_TIME = 0
    PROGRAM_START = time()
    
    #Command line parsing info
    parser = argparse.ArgumentParser(description = "Making a statistics about a pdf or txt file.")
    parser.add_argument("-p", "--pdf", nargs = 1, help = "Path to pdf file" ''', metavar = "\"*.pdf\""''')
    parser.add_argument("-t", "--txt", nargs = 1, help = "Path to txt file" ''', metavar = "\"*.txt\""''')
    parser.add_argument("-s", "--stopwords", nargs = 1, help = "Path to a file with stopwords")
    parser.add_argument("-l", "--language", nargs = 1, help = "Specifies a language for a text or PDF document", metavar = "ru/en")
    parser.add_argument("-o", "--output", nargs = 1, help = "Path to a file, which will store keywords (if needed)")
    
    if (len(sys.argv) <= 1):
        print(parser.print_help())
        exit(0)
    
    args = parser.parse_args(sys.argv[1:])
    
    if (args.pdf != None) and (args.txt != None):
        print("Error in arguments! Only one argument can be specified at the same time:", "pdf filename or txt filename\n")
        colour_print("Exiting...", colour = Fore.RED)
        exit(0)
    
    if (args.pdf == None) and (args.txt == None):
        print("No file to parse was specified!\n")
        colour_print("Exiting...", colour = Fore.RED)
        exit(0)

    input_file = None
    if (args.pdf != None):
        input_file = file(path_pdf = args.pdf[0])
    elif (args.txt != None):
        input_file = file(path_txt = args.txt[0])
    
    stopwords_file = None
    if (args.stopwords != None):
        stopwords_file = file(path_txt = args.stopwords[0])
    else:
        stopwords_file = file()

    output_file = None
    if (args.output != None):
        output_file = file(path_txt = args.output[0])
    else:
        output_file = file()
    
    lemmatizer = None
    if (args.language != None):
        lemmatizer = lemmatize(args.language[0])
    else:
        lemmatizer = lemmatize()

    print("input_file = \"{0}\"".format(input_file.path_pdf if input_file.path_pdf != None else input_file.path_txt))
    print("stopwords_file = \"{0}\"".format(stopwords_file.path_txt if stopwords_file.path_txt != None else ""))
    print("output_file = \"{0}\"".format(output_file.path_txt if output_file.path_txt != None else ""))
    print()
    
    #Getting text from PDF file, saving it to /path/to/pdf/NAME.pdf.txt
    if (input_file.path_pdf != None):
        print("Started parsing input PDF, wait for a while...")
        pdf = input_file.path_pdf
        start_time = time()
        try:
            retcode = subprocess.call(["python", "./pdf_import.py",input_file.path_pdf, input_file.path_txt])
            if (retcode != 0):
                print("Error while parsing input PDF file!")
                exit(1)
    
            end_time = time()
            print("Parsing input PDF took {0:.3f}".format(end_time - start_time), "seconds", end = "\n\n")
    
        except OSError:
            print("Error while parsing input pdf file!")
            exit(1)

    
    #Getting words from a txt file
    print("Started parsing input TXT, wait for a while...")
    start_time = time()
    text = split.get_text(input_file.path_txt)
    end_time = time()
    print("Parsing input TXT took {0:.3f}".format(end_time - start_time), "seconds", end = "\n\n")
    input_file.processed = 1
    input_file.hash()
    input_file.text = split.get_text(input_file.path_txt)

    #Getting words for deleting
    stopwords = set()
    if (stopwords_file.path_txt == None):
        pass
    else:
        print("Started parsing TXT with stopwords, wait for a while...")
        start_time = time()
        stopwords = split.get_list(stopwords_file.path_txt, enableComments = True)
        stopwords = set(stopwords)
        end_time = time()
        stopwords_file.processed = 1
        stopwords_file.text = split.get_text(stopwords_file.path_txt)
        print("Parsing TXT with stopwords took {0:.3f}".format(end_time - start_time), "seconds", end = "\n\n")
    
    print("Started getting keyword phrases")
    start_time = time()
    keywords = keywords.getKeyPhrases(text, stopwords, lemmatizer = lemmatizer.get())
    end_time = time()
    input_file.keywords = keywords

    EXTRA_TIME += time()
    if (input("Do you want to print keyword phrases? (\"y\" or \"n\"): ") != "y"):
        pass
    else:
        print("Keyword phrases, generated by RAKE (with a phrase score):")
        for phrase in keywords:
            print("\"{0}\" ==> {1:.3f}".format(phrase[0], phrase[1]))
        print()
    EXTRA_TIME -= time()
    print("Getting keyword phrases took {0:.3f}".format(end_time - start_time), "seconds", end = "\n\n")
    
    if (output_file.path_txt != None):
        out = open(output_file.path_txt, "w")
        for key in keywords:
            out.write("{0}\n".format(key[0]))
        out.close()

    '''
    Started getting shingles for an input file
    '''
    print("Started getting shingles for input file")
    start_time = time()
    input_file.words = []
    candidate_keywords = generateCandidateKeywords(input_file.text, stopwords, lemmatizer = lemmatizer.get())
    for phrases in candidate_keywords:
        for word in phrases:
            input_file.words.append(word)
    input_file.shingles = shingles.gen_shingles(input_file.words)
    end_time = time()
    if (len(input_file.shingles) == 0):
        input_file.processed = -1
        print("No shingles were built in input file")
        exit(0)
    print("Shingles were built successfully for an input file", end = "\n\n")


    '''
    Starting building query for Google, get urls for request
    '''
    query = ""
    for wordphrase in input_file.keywords:
        query += "+(" + wordphrase[0] + ")"
    print("Getting generator for links from Google")
    start_time = time()
    links = google.search(query, filetype = "pdf", pause = QUERY_PAUSE)
    end_time = time()
    print("Generator obtaining took {0:.3f}".format(end_time - start_time), end = "\n\n")

    '''

    '''

    PROGRAM_END = time() - abs(EXTRA_TIME) - PROGRAM_START
    print("\nProgram ended successfully!\nExecution time {0:.3f} seconds".format(PROGRAM_END))
    