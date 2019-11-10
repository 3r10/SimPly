n = 675567
digit = 6
nb_occurences = 0
while n>0:
	unit = n%10
	if unit==digit:
		nb_occurences = nb_occurences+1
	n = n//10
