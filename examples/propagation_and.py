a = True
b = True
c = False
# propagation : c -> b -> a
while a:
    print(a)
    print(b)
    print(c)
    a = a and b
    b = b and c
