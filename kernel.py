from math import sqrt
import time

def ssk(list1, list2, lambda_, index):
    k_1_prev = [[1 for x in range(len(list1))] for x in range(len(list1))]
    time.sleep(30)
    k_1_cur = [[0.0 for x in range(len(list1))] for x in range(len(list1))]

    k_2_prev = [[0.0 for x in range(len(list1))] for x in range(len(list1))]
    k_2_cur = [[0.0 for x in range(len(list1))] for x in range(len(list1))]

    for p in range(index):
        """
        Calculating next K``
        """
        for n in range(len(list1)):
            for m in range(len(list2)):
                if min(n, m) < index:
                    k_2_cur[n][m] = 0
                else:
                    if list1[n - 1] == list2[m - 1]:
                        k_2_cur[n][m] = lambda_ * (k_2_cur[n][m - 1] + lambda_ * k_1_prev[n - 1][m - 1])
                    else:
                        k_2_cur[n][m] = lambda_ * k_2_cur[n][m - 1]
    
    
        """
        Calculating next K`
        """
        for n in range(len(list1)):
            for m in range(len(list2)):
                if min(n, m) < index:
                    k_1_cur[n][m] = 0
                else:
                    k_1_cur[n][m] = lambda_ * k_1_cur[n - 1][m] + k_2_cur[n][m]
    
        k_1_cur, k_1_prev = k_1_prev, k_1_cur
        k_2_cur, k_2_prev = k_2_prev, k_2_cur
    
        """
        Calculating K_n(sx,t)
        Need to calculate K_n(s, t); K_n(s - 1, t); ...
        """
        k = [0.0 for x in range(len(list1) + 1)]
    
        for i in range(len(list1) + 1):
            if min(i, len(list2)) < p:
                k[i] = 0
            else:
                k[i] = k[i - 1]
                for j in range(len(list2)):
                    if list1[i - 1] == list2[j]:
                        k[i] += lambda_ * lambda_ * k_1_prev[i - 1][j]
    return(k[len(list1)])


#list1 = ["a", "b", "c", "d", "e", "f"]
#list2 = ["a", "b", "c", "f", "e", "d"]

"""
list1 = []
str1 = "science is organized knowledge"
for char in str1:
    list1.append(char)


list2 = []
str2 = "wisdom is organized life"
for char in str2:
    list2.append(char)
"""

#list1 = [1, 2, 3, 4]
#list2 = [5, 2, 3, 6]

lambda_ = 0.65
index = 6

list1 = []
file1 = open("./TMP/10.1.1.93.6473.pdf.txt")
text1 = file1.read()
file1.close()
for char in text1:
    list1.append(char)

list2 = []
file2 = open("./PDFs/10.1.1.93.6473.pdf.txt")
text2 = file2.read()
file2.close()
for char in text2:
    list2.append(char)



print(ssk(list1, list2, lambda_, index) / sqrt(ssk(list1, list1, lambda_, index) * ssk(list2, list2, lambda_, index)))


#for sublist in k_2_cur:
#    print(sublist)

#print()

#for sublist in k_1_cur:
#    print(sublist)