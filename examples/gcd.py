a = 9
b = 15
while b!=0:
    tmp = b
    b = a%b
    a = tmp
print(a)
