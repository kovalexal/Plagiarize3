#Some source code was taken from
#http://stackoverflow.com/questions/5725278/python-help-using-pdfminer-as-a-library
#

import sys
from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from cStringIO import StringIO
from pdfminer.pdfparser import PDFSyntaxError

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
    try:
        process_pdf(rsrcmgr, device, fp)
    except PDFSyntaxError:
        exit(1)
    fp.close()
    device.close()

    str = retstr.getvalue()
    retstr.close()
    return str

def get_txt(pathin, pathout):
    '''getTxt(name)
    Getting a txt file from a string str
    '''
    if (pathin.endswith(".pdf") == False):
        exit(-1)

    str = convert_pdf(pathin)
    file = open(pathout, "w")
    file.write(str)
    file.close()
    return str
  
if __name__ == "__main__":
    get_txt(sys.argv[1], sys.argv[2])
