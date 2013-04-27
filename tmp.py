import kernel

a = [x for x in range(10000)]
b = [10000 - x for x in range(10000)]

print(kernel.ssk(a, b, 0.5, 3))