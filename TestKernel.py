#!/usr/bin/env python3
from Tests import results


from config import *
from math import sqrt
import gc
import file_process
import sys

def ssk(list1, list2, lambda_, kernel_number):
    '''
    Calculates SSK for two lists
    '''
    list1_len = len(list1)
    list2_len = len(list2)

    k_1_prev = [[1.0 for x in range(list2_len + 1)] for x in range(list1_len + 1)]
    k_1_cur = [[0.0 for x in range(list2_len + 1)] for x in range(list1_len + 1)]

    k_2_prev = [[0.0 for x in range(list2_len + 1)] for x in range(list1_len + 1)]
    k_2_cur = [[0.0 for x in range(list2_len + 1)] for x in range(list1_len + 1)]
    
    k = [0.0 for x in range(list1_len + 1)]

    for p in range(1, kernel_number):
        """
        Calculating next K``
        """
        for n in range(len(list1)):
            for m in range(len(list2)):
                if min(n, m) < p:
                    k_2_cur[n][m] = 0
                else:
                    if list1[n - 1] == list2[m - 1]:
                        k_2_cur[n][m] = lambda_ * (k_2_cur[n][m - 1] + lambda_ * k_1_prev[n - 1][m - 1])
                    else:
                        try:
                            k_2_cur[n][m] = lambda_ * k_2_cur[n][m - 1]
                        except:
                            print(n, m)
                            exit(0)
    
    
        """
        Calculating next K`
        """
        for n in range(len(list1)):
            for m in range(len(list2)):
                if min(n, m) < p:
                    k_1_cur[n][m] = 0
                else:
                    k_1_cur[n][m] = lambda_ * k_1_cur[n - 1][m] + k_2_cur[n][m]
    
        k_1_cur, k_1_prev = k_1_prev, k_1_cur
        k_2_cur, k_2_prev = k_2_prev, k_2_cur
    
    """
    Calculating K_n(sx,t)
    Need to calculate K_n(s, t); K_n(s - 1, t); ...
    """        

    for i in range(len(list1) + 1):
        if min(i, len(list2)) < kernel_number:
            k[i] = 0
        else:
            k[i] = k[i - 1]
            for j in range(len(list2)):
                if list1[i - 1] == list2[j]:
                    k[i] += lambda_ * lambda_ * k_1_prev[i - 1][j]
    del k_1_prev
    del k_1_cur
    del k_2_prev
    del k_2_cur
    gc.collect()
    return(k[len(list1)])


def ssk_normalized(list1, list2, lambda_, kernel_number):
    '''
    Calculates normalized SSK for two lists
    '''
    tmp1 = ssk(list1, list2, lambda_, kernel_number)
    tmp2 = ssk(list1, list1, lambda_, kernel_number)
    tmp3 = ssk(list2, list2, lambda_, kernel_number)
    return tmp1 / sqrt(tmp2 * tmp3)
    #return ssk(list1, list2, lambda_, kernel_number) / sqrt(ssk(list1, list1, lambda_, kernel_number) * ssk(list2, list2, lambda_, kernel_number))

if __name__ == "__main__":
    lambda_ = 0.5

    min_ssk = 100

    for n in range(1, 10):
        min_ssk = 100
        simularities = {}

        for filenames in results:
            file1 = file_process.file(path_txt = "./Tests/" + filenames[0]) 
            file2 = file_process.file(path_txt = "./Tests/" + filenames[1])

            file1.text = file_process.get_text(file1)
            file1.words = file_process.get_words(file1)
            file1.words = file_process.enumerate_words(file1.words)

            file2.text = file_process.get_text(file2)
            file2.words = file_process.get_words(file2)
            file2.words = file_process.enumerate_words(file2.words)

            '''
            print("Text1:")
            print(file1.words, end = "\n\n")
            print("Text2:")
            print(file2.words, end = "\n\n")
            '''

            sim = ssk_normalized(file1.words, file2.words, lambda_, n)
            simularities[(filenames[0], filenames[1])] = sim

            '''
            print("SSK result {0:.3f}".format(sim))
            if (0 < sim < 0.190):
                print("Result: Not Plagiarize")
            else:
                print("Result: Plagiarize")
            '''
            if (results[(filenames[0], filenames[1])] == 1):
                if (sim < min_ssk):
                    min_ssk = sim
        print("{0}: {1}".format(n, min_ssk), end = " ")

        min_ssk = 0
        '''
        Counting tests
        '''
        tests = 0
        for filenames in results:
            if (results[(filenames[0], filenames[1])] == 1):
                if (simularities[(filenames[0], filenames[1])] >= min_ssk):
                    tests += 1
        print("{0}/{1}".format(tests, 95))
