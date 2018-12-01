#!/usr/bin/env python3

import os

infile = 'sandhi_words_dvnag.txt'
outfile = 'sandhi_words_wx.txt'

print("Starting conversion of file %s ..." % infile)

os.system('rm %s' % outfile)

with open(infile) as src_file:
    f_content = src_file.read()
    for every in f_content.split(' '):
        bufr = 'echo "%s" | ./utf82iscii.pl | ./ir_skt >> %s' % (every, outfile)
        os.system(bufr)
print("File (%s) converted to WX format and result stored in %s." % (infile, outfile)) 
