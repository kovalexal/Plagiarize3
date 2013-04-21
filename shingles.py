import sys
from hash import md5sum_str
from config import *

def gen_shingles(word_list):
    global SHINGLES_LEN
    shingles = []
    for i in range(len(word_list) - (SHINGLES_LEN - 1)):
        shingles.append(md5sum_str("".join( [word for word in word_list[i : i + SHINGLES_LEN]] )))
    return shingles


def compare(source1,source2):
    same = 0
    if (len(source1) > len(source2)):
        shingles1 = source2
        shingles2 = source1
    else:
        shingles1 = source1
        shingles2 = source2
    for i in range(len(shingles1)):
        if shingles1[i] in shingles2:
            same = same + 1
    #return same*2/float(len(source1) + len(source2))*100
    #print(len(source1))
    #print(len(source2))
    #return same*2/(len(source1) + len(source2))*100
    return same/min(len(source1), len(source2))*100

if __name__ == "__main__":
    #list1 = ["разум", "дан", "человеку", "того", "чтобы", "разумно", "жил", "того", "только", "чтобы"]
    #list2 = ["дан", "человеку", "того", "чтобы", "разумно", "жил", "того", "только", "чтобы", "понимал"]
    #shingles1 = gen_shingles(list1)
    #shingles2 = gen_shingles(list2)
    in1 = open("./Task/Выделение набора ключевых слов/0470749822.pdf.txt", "r")
    #in1 = open(sys.argv[1])
    text1 = in1.read()
    in1.close()
    in2 = open("./TMP/file1.pdf.txt", "r")
    #in2 = open(sys.argv[2])
    text2 = in2.read()
    in2.close()

    from split import get_list
    from keywords import generateCandidateKeywords


    words = []
    stopwords = set()
    lemmatizer = None
    candidate_keywords = generateCandidateKeywords(text1, stopwords, lemmatizer)
    for sublist in candidate_keywords:
        for word in sublist:
            words.append(word)
    shingles1 = gen_shingles(words)
    print(len(shingles1))
    exit(0)
    
    candidate_keywords = generateCandidateKeywords(text2, stopwords, lemmatizer)
    for sublist in candidate_keywords:
        for word in sublist:
            words.append(word)
    shingles2 = gen_shingles(words)
    print(len(shingles2))

    print(compare(shingles2, shingles1))
    print(compare(shingles1, shingles2))
