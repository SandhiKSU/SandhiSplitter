# SandhiSplitter
Python 3 port of University of Hyderabad's Sandhi Splitter
How to run:
	Standalone mode:
	1.	Copy splitter.py to scl/SHMT/prog/sandhi_splitter
	2.	python3 splitter.py -h for help details.
        3.      Move to sandhi_splitter directory, and execute as:
                python3 splitter.py -m ../../../morph_bin/skt_morf.bin girISa -v 1
        Batch or test case mode (to compare Python program and legacy outputs):
	4. 	Along with above setup used for standalone method, copy  
		test_cases/sandhi_words_wx.txt test_cases/test_case.sh also in scl directory
		as in point 1.
	5.	Run command as $ bash test_case.sh, output of this test will be written in file
		test_case.txt at same location.
