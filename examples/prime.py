n = 167
d = 2
is_prime = True
while d*d<=n and is_prime:
    if n%d==0:
        is_prime = False
    d = d+1
