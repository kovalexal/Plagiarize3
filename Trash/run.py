#Notes
#http://stackoverflow.com/questions/8724557/how-to-run-a-python-script-from-another-python-script-and-get-the-returned-statu
#
import sys
import parse
import subprocess
import time

pdf = sys.argv[1]
if (len(pdf) > 3) and (pdf[len(pdf) - 4:len(pdf)] == ".pdf"):
    filename = pdf[:pdf.find(".pdf")]
    txt = filename + ".txt"
    try:
        retcode = subprocess.call(["/usr/bin/python", "./pdfImport.py", pdf, txt])
        if (retcode != 0):
            exit()
    except OSError:
        print("Error!")
        exit()
else:
    txt = pdf



try:
    words = parse.getlist(txt, enableComments = False)
    rubbish = parse.getlist(sys.argv[2], enableComments = True)
except IndexError:
    print("Error in arguments!")
    exit()

rubbish = set(rubbish)

word = []
number = []

start_time = time.time()
for i in range(len(words)):
    if (words[i] not in rubbish) and (words[i] not in word):
        word.append(words[i])
        number.append(words.count(words[i]))

for v, k in reversed(sorted(zip(number, word))):
    print("{0} = {1}".format(k, v))
    
print(time.time()-start_time, "seconds")
exit()
