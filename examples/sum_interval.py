a = 134
b = 178
s = 0
i = a
while i<=b:
    s = s+i
    i = i+1
# must be True
test = s==((a+b)*(b-a+1))//2
print(test)
