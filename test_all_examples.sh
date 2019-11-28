#!/bin/sh

if [ ! -d examples.S ]
then
  mkdir examples.S
fi
if [ ! -d examples.out ]
then
  mkdir examples.out
fi
for f in examples/*.py
do
  name=`basename $f | rev | cut -c4- | rev`
  echo "------------------------------------"
  echo $f
  echo "------------------------------------"
  cat $f
  echo "------------------------------------"
  ./simply.py $f examples.S/$name.S
  arm-linux-gnueabihf-gcc -ggdb3 -nostdlib -o examples.out/$name -static examples.S/$name.S
  echo "Execution..."
  echo "------------------------------------"
  qemu-arm examples.out/$name
  echo "------------------------------------"
  echo "Type Enter to continue..."
  read z
done
