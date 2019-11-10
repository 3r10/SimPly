nombre = 91*45//2
d = 2
est_premier = True
while d*d<nombre and est_premier:
  if nombre%d==0:
    est_premier = False
  d = d+1
