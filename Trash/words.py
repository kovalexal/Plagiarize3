dictionary = {}
current_number = 0

def enumerate_words(list_):
    '''
    Enumerates words and return a list of numbers
    '''
    global dictionary, current_number
    result_list = []
    for word in list_:
        try:
            value = dictionary[word]
        except KeyError:
            value = current_number
            dictionary[word] = value
            current_number += 1
        result_list.append(value)

    return result_list

if __name__ == "__main__":
    list1 = ["a", "b", "c", "a", "c"]
    list2 = ["a", "b", "d"]
    print(enumerate_words(list1))
    print(enumerate_words(list2))