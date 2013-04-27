import sys
import argparse
import subprocess
import time

import parse

def fprintL(thefile, thelist):
	for item in thelist:
		thefile.write("%s\n" % item)

PROGRAM_START = time.time()

#Command line parsing info
parser = argparse.ArgumentParser(description = "Making a statistics about a pdf of txt file.")
parser.add_argument("-p", "--pdf", nargs = 1, help = "Path to pdf file" ''', metavar = "\"*.pdf\""''')
parser.add_argument("-t", "--txt", nargs = 1, help = "Path to txt file" ''', metavar = "\"*.txt\""''')
parser.add_argument("-g", "--garbage", nargs = 1, help = "Path to a file with a garbage")
parser.add_argument("-o", "--output", nargs = 1, help = "Path to output file")

if (len(sys.argv) <= 1):
	print(parser.print_help())
	exit()

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

if (args.garbage != None):
	garbage_file = args.garbage[0]
else:
	garbage_file = ""

if (args.output != None):
	output_file = args.output[0]
else:
	output_file = ""

print("input_file =", input_file)
print("garbage_file =", garbage_file)
print("output_file =", output_file)


#Getting text from PDF file, saving it to /path/to/pdf/NAME.pdf.txt
if (args.pdf != None):
	print("\nStarted parsing PDF, wait for a while...")
	pdf = args.pdf[0]
	start_time = time.time()
	try:
		retcode = subprocess.call(["python", "./pdfImport.py", pdf, pdf + ".txt"])
		if (retcode != 0):
			print("Error while pasing PDF file!")
			exit(1)

		end_time = time.time()
		print("Parsing PDF took {0:.3f}".format(end_time - start_time), "seconds")

	except OSError:
		print("Error while trying to parse pdf file!")
		exit(1)

#Getting words from a txt file
print("\nStarted parsing TXT, wait for a while...")
start_time = time.time()
text = parse.getlist(input_file, enableComments = False)
end_time = time.time()
print("Parsing TXT took {0:.3f}".format(end_time - start_time), "seconds")

#Getting words for deleting
if (garbage_file == ''):
	garbage = set()
	pass
else:
	#print("\nStarted parsing TXT with garbage, wait for a while...")
	start_time = time.time()
	garbage = parse.getlist(garbage_file, enableComments = True)
	end_time = time.time()
	print("\nParsing TXT with garbage took {0:.3f}".format(end_time - start_time), "seconds")
	garbage = set(garbage)

#Counting words
#print("\nStarted counting words")
start_time = time.time()
words = set(text) - garbage
words = list(words)
count = []
for i in range(len(words)):
	#count.append(text.count(words[i]))
	count.append(i)
end_time = time.time()
print("\nCounting words took {0:.3f}".format(end_time - start_time), "seconds")

#Printing statistics
start_time = time.time()
if (output_file == ''):
	for v, k in reversed(sorted(zip(count, words))):
		print("{0} = {1}\n".format(k, v))
else:
	out = open(output_file, "w")
	for v, k in reversed(sorted(zip(count, words))):
		out.write("{0} = {1}\n".format(k, v))
	out.close()

end_time = time.time()
print("\nSorting took {0:.3f}".format(end_time - start_time), "seconds")

PROGRAM_END = time.time()
print("Program ended successfully!\nExecution time {0:.3f} seconds".format(PROGRAM_END - PROGRAM_START))
