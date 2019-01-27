#!/bin/bash
#if g++ /media/nemish/College/ProjectWork/sem-6-project/compilerAPI/compilerAp/compilerApiApp/static/code.cpp -o /media/nemish/College/ProjectWork/sem-6-project/compilerAPI/compilerApi/compilerApiApp/static/abc.out;
#then
#  ./abc.out <input.txt> output.txt
#  exit
#fi
ulimit -t 6
ulimit -m 30000
/usr/bin/time -v python3 $1 < $2 > $3 2> $4
#/usr/bin/time -v $3 <$4 &> $5
exit
