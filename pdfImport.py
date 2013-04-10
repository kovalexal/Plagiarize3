#Some source code was taken from
#http://stackoverflow.com/questions/5725278/python-help-using-pdfminer-as-a-library
#

import sys
from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from cStringIO import StringIO

def convert_pdf(path):
    '''
    convert_pdf(path)
    Converts a pdf with path to a string
    '''
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)

    fp = file(path, 'rb')
    process_pdf(rsrcmgr, device, fp)
    fp.close()
    device.close()

    str = retstr.getvalue()
    retstr.close()
    return str

def getTxt(pathin, pathout):
    '''getTxt(name)
    Getting a txt file from a string str
    '''
    str = convert_pdf(pathin)
    file = open(pathout, "w")
    file.write(str)
    file.close()
  
if __name__ == "__main__":
    getTxt(sys.argv[1], sys.argv[2])
