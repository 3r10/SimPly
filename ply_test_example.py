nombre = 91
d = 2
est_premier = 1
while d*d<=nombre and est_premier!=0:
  if nombre%d==0:
    est_premier = 0
  else:
    d = d+1
