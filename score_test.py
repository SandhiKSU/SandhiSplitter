#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import subprocess

__author__ = 'Nicolas REIMEN'

# ---------------------------------------------------- Globals ---------------------------------------------------------
g_deva_2_wx_extras = [
    ('M', 'ं'),
    ('H', 'ः'),
    ('Z', 'ऽ')
]

g_deva_2_wx_maatras = [
    ('A', 'ा'),
    ('i', 'ि'),
    ('I', 'ी'),
    ('u', 'ु'),
    ('U', 'ू'),
    ('e', 'े'),
    ('E', 'ै'),
    ('o', 'ो'),
    ('O', 'ौ'),
    ('q', 'ृ'),
    ('Q', 'ॄ'),
    ('a', '')
]

g_deva_2_wx_vowels = [
    ('a', 'अ'),
    ('A', 'आ'),
    ('i', 'इ'),
    ('I', 'ई'),
    ('u', 'उ'),
    ('U', 'ऊ'),
    ('e', 'ए'),
    ('E', 'ऐ'),
    ('o', 'ओ'),
    ('O', 'औ'),
    ('q', 'ऋ'),
    ('Q', 'ॠ'),
    ('L', 'ऌ')
]

g_deva_2_wx_consonants = [
    ('k', 'क'),
    ('K', 'ख'),
    ('g', 'ग'),
    ('G', 'घ'),
    ('f', 'ङ'),
    ('c', 'च'),
    ('C', 'छ'),
    ('j', 'ज'),
    ('J', 'झ'),
    ('F', 'ञ'),
    ('t', 'ट'),
    ('T', 'ठ'),
    ('d', 'ड'),
    ('D', 'ढ'),
    ('N', 'ण'),
    ('w', 'त'),
    ('W', 'थ'),
    ('x', 'द'),
    ('X', 'ध'),
    ('n', 'न'),
    ('p', 'प'),
    ('P', 'फ'),
    ('b', 'ब'),
    ('B', 'भ'),
    ('M', 'म'),
    ('y', 'य'),
    ('r', 'र'),
    ('l', 'ल'),
    ('v', 'व'),
    ('S', 'श'),
    ('R', 'ष'),
    ('s', 'स'),
    ('h', 'ह')
]

g_deva_2_wx_halant = '्'


# ---------------------------------------------------- Functions -------------------------------------------------------
def deva_2_wx(p_deva):
    """
    Devanagari to WX converter

    :param p_deva: Devanagari input
    :return: equivalent WX string
    """
    l_wx_result = p_deva

    # single consonants
    for l_wx, l_deva in g_deva_2_wx_consonants:
        l_wx_result = re.sub(l_deva + g_deva_2_wx_halant, l_wx, l_wx_result)

    # consonant + maatra couples
    for l_wx_c, l_deva_c in g_deva_2_wx_consonants:
        for l_wx_m, l_deva_m in g_deva_2_wx_maatras:
            l_wx_result = re.sub(l_deva_c + l_deva_m, l_wx_c + l_wx_m, l_wx_result)

    # single vowels + anusvara / visarga
    for l_wx, l_deva in g_deva_2_wx_vowels + g_deva_2_wx_extras:
        l_wx_result = re.sub(l_deva, l_wx, l_wx_result)

    return l_wx_result


# ---------------------------------------------------- Main section ----------------------------------------------------
if __name__ == "__main__":
    # test file from Shivaja. Contains line of the form: X=>y+y+y...+y
    with open('sanXi_split', 'r') as l_f_in:
        # number of input lines processed so far
        l_line_count = 0

        # number of candidates proposed by the NEW program (excluding cases where no proposal is made)
        l_candidate_count = 0

        # number of successes of the NEW program
        l_success_count = 0

        # number of successes of the OLD program (UoH cpp code)
        l_success_count_old = 0

        for l_line in l_f_in.read().split('\n'):
            l_line_count += 1

            # various cleanup operations
            # remove sloka numbers & mid-sloka markers
            l_line = re.sub(r'।', '', l_line)
            l_line = re.sub(r'॥\d+॥', '', l_line)
            # normalize spaces
            l_line = re.sub(r'\s+', ' ', l_line).strip()

            # do not process empty lines
            if len(l_line) == 0:
                continue

            # start processing of the current line
            print('====================== [{0}] =================================\n'.format(l_line_count) + l_line)
            # cut up the X=>y+y+y...+y format
            l_sandhied_deva = l_line.split('=>')[0].strip()
            l_goal_deva = l_line.split('=>')[1].strip()

            # convert from Devanagari to WX
            l_sandhied = deva_2_wx(l_sandhied_deva)
            l_goal = deva_2_wx(l_goal_deva)

            # remove any non alphabetic characters
            l_sandhied = re.sub(r'[^a-zA-Z]', '', l_sandhied)
            l_goal = re.sub(r'[^a-zA-Z+]', '', l_goal)

            # l_sandhied = form with Sandhi, l_goal = the Sandhi split that should be obtained
            print('   l_sandhied  : {1} [{0}]'.format(l_sandhied_deva, l_sandhied))
            print('   l_goal      : {1} [{0}]'.format(l_goal_deva, l_goal))
            if len(l_sandhied) > 25:
                print('*** Not doing it: too long ***')
                continue

            # new program ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

            # building the commad to call the NEW program
            l_cmd = './splitter.py -s testing -m ../scl/morph_bin/all_morf.bin ' + l_sandhied
            print('   ------------ NEW ---------------')
            print('   l_cmd       : ' + l_cmd)

            # call the NEW program and get the result
            try:
                l_result = subprocess.check_output(l_cmd.split(), timeout=60)
                l_result = l_result.decode('utf-8')
            except subprocess.TimeoutExpired as e:
                print('   *** Failed (timeout expired) ***')
                l_result_old = ''
            except subprocess.CalledProcessError as e:
                print('   *** Failed (return code = {0}) ***'.format(e.returncode))
                l_result_old = ''
            except Exception as e:
                print('   *** Failed (unknown cause) ***')
                l_result_old = ''

            if re.search('No splittings found', l_result):
                # case where no Sandhi split is returned (Why does this happen so often ?)
                print('   *** Failed (no result proposed) ***')
            elif re.search('=', l_result):
                l_candidate_count += 1
                print('   --->', l_result, end='')
                # retrieval of the sandhi split value (candidate)
                # format: X=y+y+y...+y
                # y+y+y...+y is the part we want
                l_result = re.sub(r'\s+', ' ', l_result).strip()
                l_result = re.sub(r'\s=\s', '=', l_result).strip()
                l_result = re.sub(r'\s\S+$', '', l_result).strip()
                l_candidate = l_result.split('=')[1]
                print('   l_candidate :', l_candidate)

                # if the form proposed by the NEW splitting program is equal to the goal value --> success
                if l_candidate == l_goal:
                    l_success_count += 1
                    print('   === SUCCESS ===')

            # display success rate values
            print(('   candidates  : {0} / {1:.2f} % \n'
                   '   success rt. : {2} / {3:.2f} %').format(
                l_candidate_count, l_candidate_count/l_line_count*100,
                l_success_count, l_success_count/l_line_count*100))

            # old program ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

            # path to the old program directory
            g_scl_splitter_path = '../scl/SHMT/prog/sandhi_splitter'

            # write the word to be split in a temp file
            with open(g_scl_splitter_path + '/word_to_change', 'w') as l_f_word:
                l_f_word.write(l_sandhied)

            # command to call the OLD UoH Sandhi splitter
            l_cmd_old = ('{0}/sandhi_samaasa_splitter.out -t -s {0}/sandhi_words.txt {0}/sandhi_rules.txt ' +
                         '../scl/morph_bin/ all_morf.bin {0}/word_to_change 4').format(g_scl_splitter_path)
            print('   ------------ OLD ---------------')
            print('   l_cmd_old   :' + l_cmd_old)

            # call the OLD program and get the result
            try:
                l_result_old = subprocess.check_output(l_cmd_old.split(), stderr=subprocess.STDOUT, timeout=60)
                l_result_old = l_result_old.decode('utf-8')
            except subprocess.TimeoutExpired as e:
                print('   *** Failed (timeout expired) ***')
                l_result_old = ''
            except subprocess.CalledProcessError as e:
                print('   *** Failed (return code = {0}) ***'.format(e.returncode))
                l_result_old = ''
            except Exception as e:
                print('   *** Failed (unknown cause) ***')
                l_result_old = ''

            # the result may be more than one line long
            for l_result_line in l_result_old.split('\n'):
                l_result_line = l_result_line.strip()
                # eliminate error message (Why is this message happening ?)
                if re.search('Permission denied', l_result_line) or len(l_result_line) == 0:
                    continue

                print('   ---> ' + l_result_line)

                # get the candidate split value
                l_result_line = re.sub(r'\s+', ' ', l_result_line).strip()
                l_result_line = re.sub(r'\s=\s', '=', l_result_line).strip()
                l_result_line = re.sub(r'\s\S+$', '', l_result_line).strip()
                l_cand_old = l_result_line.split('=')[1]
                print('   l_cand_old  :', l_cand_old)

                # check for success
                # if the program proposes several values and one is correct, it is considered a success
                if l_cand_old == l_goal:
                    l_success_count_old += 1
                    print('   === SUCCESS ===')

            # display success rate for the OLD program
            print('   success rt. : {0} / {1:.2f} %'.format(
                l_success_count_old, l_success_count_old/l_line_count*100), flush=True)

