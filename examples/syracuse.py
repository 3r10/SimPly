x = 9
# flight time
flight = 0
while x!=1: # should finish
  if x%2==0:
    x = x//2
  else:
    x = 3*x+1
  print(x)
  flight = flight+1
print(flight)
