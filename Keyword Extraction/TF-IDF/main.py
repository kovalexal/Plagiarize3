import math
#import parse

words = []
count = []
#words_in_text = SOME_NUMBER
dictionary = {"hello" : 5}


def words_count(dict):
	"""
	Counting quantity of words in a dictionary
	"""
	if (len(dict) == 0):
		return 0
	words = list(dict)
	count = [dict[words[i]] for i in range(len(words))]
	quant = 0
	for i in range(len(count)):
		quant += count[i]
	return count

def tf(word, words_in_text, dict):
	"""
	Getting a term frequency for a word "word" in a text with a length
	words_in_text or from a dictionary
	"""
	if (len(dict) == 0): #returns -1 if dict is empty - possible dividing by a zero
		return -1
	if ((word not in dict) and (words_in_text != 0)): 
		return 0
	return (dict[word] / words_in_text)

def idf(word, *DOCS):
	"""
	Getting a inverse document frequency for a word "word"
	in a collection (corpus) of documents DOCS (a *DOCS pointer
	should contain a list of or dictionarys (or sets) of words in each document)
	"""
	if (word == ''): #returns -1 because of dividing by zero
		return -1
	D = len(DOCS)
	count = 0
	for i in range(D):
		if (word in DOCS[i]):
			count += 1
	if (count == 0): #returns -1 because of dividing by zero
		return -1
	return math.log((D / count))

def tf_idf(word, words_in_text, dict, *DOCS):
	"""
	Getting Term Frequency-Inverse Document Frequency - importance of a word in a collection
	"""
	return (tf(word, words_in_text, dict) * idf(word, *DOCS))


print(tf("hello", words_in_text = 1, dict = dictionary))