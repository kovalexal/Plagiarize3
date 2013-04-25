from config import *
from math import sqrt

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
    return(k[len(list1)])


def ssk_normalized(list1, list2, lambda_, kernel_number):
    '''
    Calculates normalized SSK for two lists
    '''
    return ssk(list1, list2, lambda_, kernel_number) / sqrt(ssk(list1, list1, lambda_, kernel_number) * ssk(list2, list2, lambda_, kernel_number))

if __name__ == "__main__":

    list1 = []
    str1 = "science is organized knowledge"
    for char in str1:
        list1.append(char)


    list2 = []
    str2 = "wisdom is organized life"
    #str2 = "science is organized knowledge"
    for char in str2:
        list2.append(char)

    lambda_ = 0.5

    for kernel_number in range(1, 7):
        print("{0:.3f}".format(ssk_normalized(list1, list2, lambda_, kernel_number)))

