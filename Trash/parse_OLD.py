"""Module for getting words from a file"""

import sys
import re

ENalpha = r"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
RUalpha = r"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
FRalpha = r"éèàùêâôîûëïüÿçœæ"
DEalpha = r"ÄäÖöÜüß"
digits = r"0123456789"
matching_characters = '[' + "^" + ENalpha + RUalpha + FRalpha + DEalpha + "'" + '-' + ']'

def getlist(filename, enableComments = True, sorted = False, lowerCase = True):
    """
    Getting a list with all words from a file.
    Ignoring numbers, switching to lower case
    If enableComments argument is True (by-default), ignoring comments, started with #
    """
    #Trying to open a file, with a filename
    try:
        f = open(filename, 'r')
    except IOError:
        print("Not found file \"{0}\"".format(filename))
        return []
    list = []
    #Reading and getting words from file
    for line in f:
        str = line
        if (enableComments == True):
            str = line[:line.find("#")]
        tmp = re.split(matching_characters, str)
        #Deleting NULL-strings
        for i in range(tmp.count("")):
            tmp.remove("")
        list.extend(tmp)
    if (sorted == True):
        list.sort()
    #Switching to lower-case (if needed)
    if (lowerCase == True):
        for i in range(len(list)):
            list[i] = list[i].lower()
    f.close()
    if (sorted == True):
        list.sort()
    return list

