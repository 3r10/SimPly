x = False
y = False
z = True
# propagation : z -> y -> x
while not x:
    x = x or y
    y = y or z
