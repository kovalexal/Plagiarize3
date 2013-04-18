"""Module for working with a file"""

import sys
import re

text = {}
delimeters = set({".", ",", "!", "?", "(", ")", "{", "}", "[", "]", ":", ";", "-", "--", "”", "%", '––', '…', "/"})

def get_text(filename):
    """
    Getting a text from a file
    """
    try:
        f = open(filename, "r")
    except FileNotFoundError:
        print("Not found file \"{0}\"".format(filename))
        return ""
    text = f.read()
    f.close()
    return text

def get_list(filename, enableComments = True, sorted = False, lowerCase = True):
    """
    Getting a list with all words from a file.
    Ignoring numbers, switching to lower case
    If enableComments argument is True (by-default), ignoring comments,started with #
    """
    global text, delimeters
    str = get_text(filename)
    text[filename] = str
    if (lowerCase == True):
        str = str.lower()
    if (enableComments == True):
    	comments = re.compile(r"(#.*)", re.UNICODE)
    	str = comments.sub(r"", str)
    tmplist = re.split("[^a-zA-Z0-9а-яА-Я_-]", str)
    wordlist = []

    for word in tmplist:
        if (word not in delimeters):
            wordlist.append(word)
    
    if (sorted == True):
    	wordlist.sort()
    return wordlist

'''
def split_paragraphs(filename):
    """
    Splits text into paragraphs
    """
    if (filename not in text):
        text[filename] = get_text(filename)
    paragraphs = re.split(r"\n{2,}", str)
    return paragraphs

def split_sentences(str):
    """
    Splits paragraphs into sentences
    """
    sentences = re.split(r"[\.\?\!]", str)
    return sentences

def split_words(str):
    """
    Splits sentences into list of words
    """
    sentence = re.split("[^a-zA-Z0-9а-яА-Я_-]", str)
    return sentence

def split_by_rubbish(words_sequence, rubbish):
    """
    Splits words sequence by rubbish
    """
    potential_keywords = []
    tmp = []
    for i in range(len(words_sequence)):
        if(words_sequence[i] in rubbish and tmp != []):
            potential_keywords.append(tmp)
            tmp = []
        else:
            if (words_sequence[i] in rubbish and tmp == []):
                tmp = []
            else:
                tmp.append(words_sequence[i])
    if (tmp != []):
        potential_keywords.append(tmp)
    return potential_keywords
'''
