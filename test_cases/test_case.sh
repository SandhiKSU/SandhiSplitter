#!/usr/bin/env bash

# Written by Ramanuj Pandey [ ramanuj.p7@gmail.com ]

# This file need to be copied to scl/SHMT/prog/sandhi_splitter dir to work
# Very basic type, created only to compare output from Python and CPP code.

# Optimizations and enhancements pending.

rm -f test_case.txt
cur_dir=`pwd`

if [ "`basename $cur_dir`" != "sandhi_splitter" ]; then
	echo "$0 need top run under scl/SHMT/prog/sandhi_splitter"
	exit 1
fi

while read name; do 
    if [ ! -z $name ]; then
        echo "Doing sandhi splitt for: $name"
	echo "Python program output:" >> test_case.txt
        python3 splitter.py -m ../../../morph_bin/skt_morf.bin $name >> test_case.txt
	echo "CPP program output:" >> test_case.txt
        echo $name > ./word_to_change
        ./sandhi_samaasa_splitter.out -t -s ./sandhi_words.txt ./sandhi_rules.txt ../../../morph_bin/skt_morf.bin ./word_to_change 4 >> test_case.txt
    fi
done < sandhi_words_wx.txt
