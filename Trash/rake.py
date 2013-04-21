# Adapted from: github.com/aneesha/RAKE/rake.py
# Taken from: http://sujitpal.blogspot.ru/2013/03/implementing-rake-algorithm-with-nltk.html

import operator
import nltk
import string

def isPunct(word):
  return len(word) == 1 and word in string.punctuation

def isNumeric(word):
  try:
    float(word) if '.' in word else int(word)
    return True
  except ValueError:
    return False

class RakeKeywordExtractor:

  def __init__(self):
    self.stopwords = set(nltk.corpus.stopwords.words())
    self.top_fraction = 1 # consider top third candidate keywords by score

  def _generate_candidate_keywords(self, sentences):
    phrase_list = []
    for sentence in sentences:
      words = ["|" if x in self.stopwords else x for x in nltk.word_tokenize(sentence.lower())]
      phrase = []
      for word in words:
        if word == "|" or isPunct(word) or isNumeric(word):
          if len(phrase) > 0:
            phrase_list.append(phrase)
            phrase = []
        else:
          phrase.append(word)
    return phrase_list

  def _calculate_word_scores(self, phrase_list):
    word_freq = nltk.FreqDist()
    word_degree = nltk.FreqDist()
    for phrase in phrase_list:
      degree = len([x for x in phrase if not isNumeric(x)]) - 1
      for word in phrase:
        word_freq.inc(word)
        word_degree.inc(word, degree) # other words
    for word in list(word_freq.keys()):
      word_degree[word] = word_degree[word] + word_freq[word] # itself
    # word score = deg(w) / freq(w)
    word_scores = {}
    for word in list(word_freq.keys()):
      word_scores[word] = word_degree[word] / word_freq[word]
    return word_scores

  def _calculate_phrase_scores(self, phrase_list, word_scores):
    phrase_scores = {}
    for phrase in phrase_list:
      phrase_score = 0
      for word in phrase:
        phrase_score += word_scores[word]
      phrase_scores[" ".join(phrase)] = phrase_score
    return phrase_scores
    
  def extract(self, text, incl_scores=False):
    sentences = nltk.sent_tokenize(text)
    phrase_list = self._generate_candidate_keywords(sentences)
    word_scores = self._calculate_word_scores(phrase_list)
    phrase_scores = self._calculate_phrase_scores(
      phrase_list, word_scores)
    sorted_phrase_scores = sorted(iter(phrase_scores.items()),
      key=operator.itemgetter(1), reverse=True)
    n_phrases = len(sorted_phrase_scores)
    if incl_scores:
      return sorted_phrase_scores[0:int(n_phrases/self.top_fraction)]
    else:
      return [x[0] for x in sorted_phrase_scores[0:int(n_phrases/self.top_fraction)]]

def test(text):
  rake = RakeKeywordExtractor()
  keywords = rake.extract(text, incl_scores = False)
  '''keywords = rake.extract("""
Compatibility of systems of linear constraints over the set of natural 
numbers. Criteria of compatibility of a system of linear Diophantine 
equations, strict inequations, and nonstrict inequations are considered. 
Upper bounds for components of a minimal set of solutions and algorithms 
of construction of minimal generating sets of solutions for all types of 
systems are given. These criteria and the corresponding algorithms for 
constructing a minimal supporting set of solutions can be used in solving 
all the considered types of systems and systems of mixed types.
  """, incl_scores=True)
'''
  for keyword in keywords[:10]:
    print(keyword)
  exit(0)
  print(keywords[:10])
  
if __name__ == "__main__":
  import sys
  input_file = open(sys.argv[1], "r")
  input_text = input_file.read()
  test(input_text)