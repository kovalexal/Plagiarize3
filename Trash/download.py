import urllib
import sys

def dlProgress(count, blockSize, totalSize):
    percent = int(count*blockSize*100/totalSize)
    sys.stdout.write("\r" + rem_file + "...%d%%" % percent)
    sys.stdout.flush()


def download(url = '', output = ''):
	rem_file = url
	loc_file = rem_file.split('/')[-1]
	urllib.urlretrieve(rem_file, loc_file, reporthook=dlProgress)
