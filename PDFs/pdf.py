import sys
from PyPDF2 import PdfFileReader 
 
def convertPdf2String(path):
    content = ""
    # load PDF file
    file = open(path, "rb")
    pdf = PdfFileReader(file)
    # iterate pages
    for i in range(0, pdf.getNumPages()):
        # extract the text from each page
        content += pdf.getPage(i).extractText() + " n"
    # collapse whitespaces
    content = " ".join(content.replace("xa0", " ").strip().split())
    return content
 
# convert contents of a PDF file and store retult to TXT file
f = open(sys.argv[1]+'.txt','w+')
f.write(convertPdf2String(sys.argv[1]))
f.close()
