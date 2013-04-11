from download import download
import google

class file:
    def __init__(self, url = "", path = ""):
        self.url = url
        self.path = path
        
f = open("output")
keyphrases = f.readlines()
f.close()

query = ''
for tmp in keyphrases:
    query += "+(" + tmp[:-1] + ")"
query += " filetype:pdf"

urls = google.find(query, 3)

#for url in urls:
    #print(url)

files = []
for url in urls:
    f = file(url, download(url, directory = "./TMP"))
    files.append(f)

for f in files:
    print(f.url)
    print(f.path)
    print()