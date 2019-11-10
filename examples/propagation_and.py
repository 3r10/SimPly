a = True
b = True
c = False
# propagation : c -> b -> a
while a:
    a = a and b
    b = b and c
