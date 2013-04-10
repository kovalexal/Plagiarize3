import os
import glob
import sys
from PyPDF2 import PdfFileReader
#import pyPdf
 
#parent = "C:/Users/victoryee/Google Drive/Projects/extract-pdf-text"
#os.chdir(parent)
#filename = os.path.abspath('naacl06-shinyama.pdf')
 
def getPDFContent(path):
    content = ""
    # Load PDF into pyPDF
    file = open(path, "rb")
    pdf = PdfFileReader(file)
    # Iterate pages
    for i in range(0, pdf.getNumPages()):
        # Extract text from page and add to content
        content += pdf.getPage(i).extractText() + "/n"
    # Collapse whitespace
    content = " ".join(content.replace("/xa0", " ").strip().split())
    return content
 
# print getPDFContent(filename).encode("ascii", "ignore")
#print getPDFContent(filename = "~/Desktop/Plagiarise3/PDFs/UTF8.pdf").encode("ascii", "xmlcharrefreplace")
print(getPDFContent(sys.argv[1]))
