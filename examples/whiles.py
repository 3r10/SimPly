x = 19
# double loop
while x>2:
    while x%2==0:
        x = x//2
        print(x)
    x = x+1
    print(x)
print(x)
