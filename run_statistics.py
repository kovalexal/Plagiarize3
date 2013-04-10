import sys
import argparse
import subprocess
import time

import split
import stem

PROGRAM_START = time.time()

#Command line parsing info
parser = argparse.ArgumentParser(description = "Making a statistics about a pdf or txt file.")
parser.add_argument("-p", "--pdf", nargs = 1, help = "Path to pdf file" ''', metavar = "\"*.pdf\""''')
parser.add_argument("-t", "--txt", nargs = 1, help = "Path to txt file" ''', metavar = "\"*.txt\""''')
parser.add_argument("-s", "--stopwords", nargs = 1, help = "Path to a file with a stopwords")
parser.add_argument("-l", "--language", nargs = 1, help = "Specifies a language for a text or PDF document", metavar = "RUS/ENG")
parser.add_argument("-o", "--output", nargs = 1, help = "Path to output file")

if (len(sys.argv) <= 1):
	print(parser.print_help())
	exit(0)

args = parser.parse_args(sys.argv[1:])

if (args.pdf != None) and (args.txt != None):
	print("Error in arguments! Only one argument can be specified at the same time:", "pdf filename or txt filename")
	exit(0)

if (args.pdf == None) and (args.txt == None):
	print("No file to parse was specified!")
	exit(0)

if (args.txt != None):
	input_file = args.txt[0]
else:
	input_file = args.pdf[0] + ".txt"

if (args.stopwords != None):
	stopwords_file = args.stopwords[0]
else:
	stopwords_file = ""

if (args.output != None):
	output_file = args.output[0]
else:
	output_file = ""

lemmatizer = 0
languages = set({"RUS", "ENG"})
if (args.language != None and (args.language[0] in languages)):
    language = args.language[0]
    lemmatizer = None
    if (language == "RUS"):
        lemmatizer = stem.lemmatize_ru
    if (language == "ENG"):
        lemmatizer = stem.lemmatize_en
    else:
        lemmatizer = None
else:
    lemmatizer = None

print("input_file =", input_file)
print("stopwords_file =", stopwords_file)
print("output_file =", output_file)


#Getting text from PDF file, saving it to /path/to/pdf/NAME.pdf.txt
if (args.pdf != None):
	print("\nStarted parsing PDF, wait for a while...")
	pdf = args.pdf[0]
	start_time = time.time()
	try:
		retcode = subprocess.call(["python", "./pdfImport.py", pdf, pdf + ".txt"])
		if (retcode != 0):
			print("Error while parsing PDF file!")
			exit(1)

		end_time = time.time()
		print("Parsing PDF took {0:.3f}".format(end_time - start_time), "seconds")

	except OSError:
		print("Error while trying to parse pdf file!")
		exit(1)

#Getting words from a txt file
print("\nStarted parsing TXT, wait for a while...")
start_time = time.time()
text = split.get_list(input_file, enableComments = False)
end_time = time.time()
print("Parsing TXT took {0:.3f}".format(end_time - start_time), "seconds")

#Getting words for deleting
if (stopwords_file == ''):
	stopwords = set()
	pass
else:
	#print("\nStarted parsing TXT with stopwords, wait for a while...")
	start_time = time.time()
	stopwords = split.get_list(stopwords_file, enableComments = True)
	end_time = time.time()
	print("\nParsing TXT with stopwords took {0:.3f}".format(end_time - start_time), "seconds")
	stopwords = set(stopwords)

#Counting words - in dictionary
words_in_text = 0
print("\nStarted counting words")
start_time = time.time()
words = set(text) - stopwords
words = list(words)
dictionary = {word : 0 for word in words}

for word in text:
	if (word in dictionary):
		dictionary[word] = dictionary[word] + 1
		#words_in_text += 1

#Starting lemmatizing words
tmpdict = {}
for key in dictionary.keys():
    if (lemmatizer != None):
        lemm_key = lemmatizer(key)  
    else:
        lemm_key = key
    if (lemm_key not in tmpdict):
        tmpdict[lemm_key] = dictionary[key]
        words_in_text += dictionary[key]
    else:
        tmpdict[lemm_key] += dictionary[key]
        words_in_text += dictionary[key]

dictionary = tmpdict
#count = [dictionary[word] for word in words]

#count = [dictionary[words[i]] for i in range(len(words))]
end_time = time.time()
print("\nCounting words took {0:.3f}".format(end_time - start_time), "seconds")
print("Words in text without stopwords: {0}".format(words_in_text))


#Counting words - in a list (SLOW)
#print("\nStarted counting words")
#start_time = time.time()
#words = set(text) - stopwords
#words = list(words)
#count = []
#for i in range(len(words)):
#	count.append(text.count(words[i]))
#	#count.append(i)
#end_time = time.time()
#print("\nCounting words took {0:.3f}".format(end_time - start_time), "seconds")

#Printing statistics
start_time = time.time()
if (output_file == ''):
	#for v, k in reversed(sorted(zip(count, words))):
		#print("{0} = {1}\n".format(k, v))
	for v, k in reversed(sorted(zip(dictionary.values(), dictionary.keys()))):
		print("{0} = {1}\n".format(k, v))
else:
	out = open(output_file, "w")
	#for v, k in reversed(sorted(zip(count, words))):
		#out.write("{0} = {1}\n".format(k, v))
	for v, k in reversed(sorted(zip(dictionary.values(), dictionary.keys()))):
		out.write("{0} = {1}\n".format(k, v))
	out.close()

end_time = time.time()
print("\nSorting took {0:.3f}".format(end_time - start_time), "seconds")

PROGRAM_END = time.time()
print("Program ended successfully!\nExecution time {0:.3f} seconds".format(PROGRAM_END - PROGRAM_START))
