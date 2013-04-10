import sys
import pyPdf

def convertPdf2String(path):
    content = ""
    # load PDF file
    file = open(path, "rb")
    pdf = pyPdf.PdfFileReader(file)
    # iterate pages
    for i in range(0, pdf.getNumPages()):
        # extract the text from each page
        content += pdf.getPage(i).extractText() + " \n"
    # collapse whitespaces
    content = " ".join(content.replace("\xa0", " ").strip().split())
    #content = u" ".join(content.replace(u"\xa0", u" ").strip().split())
    return content

# convert contents of a PDF file and store retult to TXT file
#f = open('a.txt','w+')
#f.write(convertPdf2String(sys.argv[1]).encode("ascii", "xmlcharrefreplace"))
#f.close()

# or print contents to the standard out stream
#str = convertPdf2String("test.pdf").encode("ascii", "xmlcharrefreplace")
#str = convertPdf2String("test.pdf").encode("utf-8")
#print(str)

def convertPdf2Txt(pathin, pathout):
    content = ""
    file = open(pathin, "rb")
    pdf = pyPdf.PdfFileReader(file)
    for i in range(pdf.getNumPages()):
        content += pdf.getPage(i).extractText() + ' \n'
    file.close()
    file = open(pathout, "w")
    file.write(content)
    file.close()
    return

convertPdf2Txt(sys.argv[1], sys.argv[2])
