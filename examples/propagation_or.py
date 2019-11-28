x = False
y = False
z = True
# propagation : z -> y -> x
while not x:
    print(x)
    print(y)
    print(z)
    x = x or y
    y = y or z
