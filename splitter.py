#!/usr/bin/env python3

'''
Revision        By                                      Changes
---------------------------------------------------------------
0.0.1           Ramanuj Pandey[ramanuj.p7@gmail.com]    Ported whole to code to Python3
                                                        from CPP, level one optimization 
                                                        on code done which reduces source
                                                        lines to less than half.

License
-------
Same as original CPP code.
'''

'''
TODO: Change variable names and functions to more meaningful ones,
      Initially I didnt changed them to keep my porting easy when
      comparing to original source.
'''

import os
import sys
import logging
import argparse

pgm_ver = '0.0.1-beta'

saparator = '\t'
rules = {}
words = {}
weights = {}
check = 0
index = [0,]
no_of_splits = [0,]
split = []
rule_applied = ['',]
new_splits = []
new_rule_applied = []
initial = 0
op = {}
costs = {}
final_costs = []
output1 = {}

temp_result_file='temp_result'
ltproc_bin = '/usr/bin/lt-proc'
morph_bin  = '../../../morph_bin/skt_morf.bin'
temp_res_intrm_file = 'temp_result_mo'
res_file = 'result'


input_files = {'sandhi':('sandhi_rules.txt', 'sandhi_words.txt','skt_morf.bin'),
               'samasa':('samAsa_rules.txt', 'samAsa_words.txt','skt_samAsanoun_morf.bin'),
               'both':('all_rules.txt', 'word_freq.txt','all_morf.bin')
              }

'''
 Datastructure selection thoughts:

 1.	We need a better searchable datastructure as search happens very frequently 
	to find words and their expansion.
 2. 	We need dict item to be a list so that we can add components, as for same result many
	expansions are possible.

 With above considerations, rule db is a dictonary which has value as a list.

'''

def load_rules_and_words(rules_file, words_file):
    logging.info("Rule loader called with option: (" + rules_file +', ' + words_file + ')')
    global saparator
    rules['tot_freq'] = 0
    rule_val_extra = ''
    # If we load with default utf encoding some strings from file fail to load.
    with open(rules_file, encoding='latin-1') as fr:
      for line in fr:
         line_by_line = line.strip().split('{}'.format(saparator))
         rules['tot_freq'] += int(line_by_line[2])

    with open(rules_file, encoding='latin-1') as fr:
      for line in fr:
         line_by_line = line.strip().split('{}'.format(saparator))
         rule_index = line_by_line[0]
         rule_val   = line_by_line[1]
         if args.choice == 'sandhi':
            weights[rule_val+'='+rule_index] = int(line_by_line[2])/rules['tot_freq']
         elif args.choice == 'samasa':
            rule_val = rule_val.split('+')[0]+"-+"+rule_val.split('+')[1]+'='+rule_index
            weights[rule_val] = int(line_by_line[2])/rules['tot_freq']
         elif args.choice == 'both':
            rule_val_extra = rule_val.split('+')[0]+"-+"+rule_val.split('+')[1]+'='+rule_index
            weights[rule_val_extra] = int(line_by_line[2])/rules['tot_freq']
            weights[rule_val+'='+rule_index[0]] = int(line_by_line[2])/rules['tot_freq']

         if rule_index in rules.keys():
            rules[rule_index].append(rule_val)
            if rule_val_extra != '':
               rules[rule_index].append(rule_val_extra)
         else:
            rules[rule_index] = [rule_val]
            if rule_val_extra != '':
               rules[rule_index] = [rule_val_extra]

    saparator = ' '
    words['corpus_size'] = 0
    with open(words_file, encoding='latin-1') as fr:
      for line in fr:
         line_by_line = line.strip().split('{}'.format(saparator))
         words[line_by_line[1]] = line_by_line[0]
         words['corpus_size'] += 1

def split_word(input_word):
    global check, index, no_of_splits, split, rule_applied, rules
    first = 0
    split.append(input_word[0])
    while check == 0:
        check = 1
        temp_split = []
        temp_index = []
        temp_no_of_splits = []
        temp_rule_applied = []
        for split_cntr in range(0, len(split)):
            if no_of_splits[split_cntr] <= 4:
                if index[split_cntr] >= len(input_word):
                    temp_split.append(split[split_cntr])
                    temp_index.append(index[split_cntr])
                    temp_no_of_splits.append(no_of_splits[split_cntr])
                    temp_rule_applied.append(rule_applied[split_cntr])
                else:
                    one_char_tok = input_word[index[split_cntr]]
                    two_char_tok = input_word[index[split_cntr] : (index[split_cntr] + 2)]
                    tre_char_tok = input_word[index[split_cntr] : (index[split_cntr] + 3)]
     
                    tokens=[one_char_tok, two_char_tok, tre_char_tok]
     
                    if first == 0:
                        temp_split.append(one_char_tok)
                    else:
                        temp_split.append(split[split_cntr]+one_char_tok)
     
                    temp_index.append(index[split_cntr]+1)
                    temp_no_of_splits.append(no_of_splits[split_cntr])
                    temp_rule_applied.append(rule_applied[split_cntr])
     
                    if index[split_cntr] + 1 < len(input_word):
                        check = 0
     
                    for token in tokens:
                        if token in rules.keys():
                            for rule_cntr in range(0, len(rules[token])):
                                sutra = rules[token][rule_cntr]
                                if first == 0:
                                    temp_split.append(sutra)
                                else:
                                    temp_split.append(split[split_cntr] + sutra)
     
                                temp_index.append(index[split_cntr] + len(token))
                                temp_no_of_splits.append(no_of_splits[split_cntr]+1)
                                temp_rule_applied.append(rule_applied[split_cntr]+sutra+"="+token+"|");
     
                                if index[split_cntr] + 1 < len(input_word):
                                    check = 0
        first = 1
        split = temp_split
        index = temp_index
        no_of_splits = temp_no_of_splits
        rule_applied = temp_rule_applied

def split_final():
    vechar = []
    vechar1 = []
    output = {}
    global new_splits, new_rule_applied, initial, temp_result_file, op, res_file

    for cntr in range(0, len(split)):
        split_word = split[cntr]
     
        if split_word[-2] != '+':
            rule_token = rule_applied[cntr]
            pada_list = split_word.split('+')
            rule_list = rule_token[:-1].split('|')
            vechar.append(pada_list)
            vechar1.append(rule_list)
            for p in pada_list:
                output[p] = 1
     
    new_splits = vechar
    new_rule_applied = vechar1
        
    initial=initial + len(split)
    with open(temp_result_file, mode='wt', encoding='utf-8') as myfile:
        myfile.write('\n'.join(output.keys()))
        myfile.write('\n')

    cmd_buf = "%s -c %s < %s > %s; grep '*' %s > %s" % (ltproc_bin, morph_bin, temp_result_file,
                                                    temp_res_intrm_file, temp_res_intrm_file, 
                                                    res_file)
    logging.info("Going to call ltproc as: " + cmd_buf)
    if os.system(cmd_buf):
        logging.error("Executing command (%s) failed" % cmd_buf)
        sys.exit(1)

    with open(res_file) as myfile:
        content = myfile.readlines()

    for val in content:
        op[val.split('/')[0].split('^')[1]] = 1

def calculate_costs():
    global tot_cost, costs, final_costs, output1, op
    output = op
    tot_cost = [1] * len(new_splits)
    for cntr in range(1, len(new_splits)):
        flag = 0
        for k in range(0, len(new_splits[cntr]) -1):

            if not new_splits[cntr][k] in output.keys():
               output[new_splits[cntr][k]] = 0
            if not new_splits[cntr][k+1] in output.keys():
               output[new_splits[cntr][k+1]] = 0

            if ((output[new_splits[cntr][k]] == 1) or (output[new_splits[cntr][k+1]] == 1)):
                logging.debug("Got %s  or %s in ouput keys" % (new_splits[cntr][k],new_splits[cntr][k+1]))
                flag = 1
                break
            else:
                if new_splits[cntr][k][:-1] == '-':
                    val = new_splits[cntr][k].split('-')
                    if not words[val[0]]:
                        tot_cost[cntr] = tot_cost[cntr] * (1 / (words['corpus_size'] * 1.0) ) * weights[new_rule_applied[cntr][k]]
                    else:
                        tot_cost[cntr] = tot_cost[cntr] * (words[val[0]] / words['corpus_size'] * 1.0 ) * weights[new_rule_applied[cntr][k]]
                else:
                    if not new_splits[cntr][k] in words.keys():
                        tot_cost[cntr] = tot_cost[cntr] * (1 / (words['corpus_size'] * 1.0) ) * weights[new_rule_applied[cntr][k]]
                        logging.debug("1 Total cost is %s for %s" % (tot_cost[cntr], new_splits[cntr][k]))
                    else:
                        tot_cost[cntr] = tot_cost[cntr] * (int(words[new_splits[cntr][k]]) / words['corpus_size'] * 1.0 ) * weights[new_rule_applied[cntr][k]]
                        logging.debug("1.5 Total cost is %s for %s" % (tot_cost[cntr], new_splits[cntr][k]))
     
        if not (new_splits[cntr][-1] in words.keys()):
            tot_cost[cntr] = tot_cost[cntr] * (1 / (words['corpus_size'] * 1.0))
            logging.debug("2 Got %s  %s in ouput keys" % (new_splits[cntr][-1], tot_cost[cntr]))
        else:
            tot_cost[cntr] = tot_cost[cntr] * ((int(words[new_splits[cntr][-1]]) / (words['corpus_size'] * 1.0 )))
            logging.debug("3 Got %s  %s in ouput keys" % (new_splits[cntr][-1], tot_cost[cntr]))
            
        if not flag:
            logging.debug("Came in cost updater.")
            tot_cost[cntr] = tot_cost[cntr] / (len(new_splits[cntr]))
            if not (tot_cost[cntr] in costs.keys()):
                final_costs.append(tot_cost[cntr])
                costs[tot_cost[cntr]] = 1
            if tot_cost[cntr] in output1.keys():
                output1[tot_cost[cntr]].append(new_splits[cntr])
            else:
                output1[tot_cost[cntr]] = [new_splits[cntr],]
    logging.debug(tot_cost)        
    if not len(output1):
        if args.switch == "compare":
            print("%s\t=>\t%s" % (args.word, args.word))
        else:
            print("%s\t=>No splittings found" % args.word)
            print("%s\t=>\t0" % args.word)

def is_readable(binary):
   return os.path.isfile(binary) and os.access(binary, os.R_OK)

def is_executable(binary):
   return os.path.isfile(binary) and os.access(binary, os.X_OK)

def is_writable(binary):
   return os.path.isfile(binary) and os.access(binary, os.W_OK)

parser = argparse.ArgumentParser(description='Sandhi splitting program:\nVersion: %s.' % pgm_ver)
parser.add_argument('-c', '--choice', nargs = '?', choices=('sandhi', 'samasa', 'both'), default = 'sandhi', help = "Choose what openration to do.")
parser.add_argument('-m', '--morphbin', required=True, help='Path of morph binary to use.')
parser.add_argument('-o', '--output', help='Result should be written to this file.')
parser.add_argument('-s', '--switch', nargs = '?', choices=('compare', 'testing'), default = 'testing', help = "Choose the right switch.")
parser.add_argument('-v', '--verbose', type=int, choices=[1,2], help='Adjust verbocity level.')
parser.add_argument('word', nargs='?', help='Word to split.')
args = parser.parse_args()

if not args.verbose:
    logging.basicConfig(level=logging.WARNING)
elif args.verbose == 1:
    logging.basicConfig(level=logging.INFO)
elif args.verbose == 2:
    logging.basicConfig(level=logging.DEBUG)

logging.info("Arguments to program status: \n %s" % args)
logging.info("This run is for: " + args.choice)

''' Load rules '''
optn_selected = input_files[args.choice]
load_rules_and_words(optn_selected[0], optn_selected[1])
''' Load rule ends'''

''' Sanity begins '''
# Not doing sanity on rule and word files as we are not taking these from user now.
if not args.output:
   logging.info("Will use default file name and location.")

if not is_readable(args.morphbin):
   logging.error("Morph bin not reable, Exiting...")
   sys.exit(1)

if not (is_readable(optn_selected[0]) and is_readable(optn_selected[1])):
   logging.error("Check rules and word file, Exiting...")
   sys.exit(1)

if not args.word:
   logging.error("Provide word to split. Exiting...")
   sys.exit(2)

''' Sanity ends '''

logging.info("Loaded corpus size: %d" % words['corpus_size'])
logging.info("Total frequency of rules: %d" % rules['tot_freq'])
logging.debug("Loaded rules: %s " % rules)
logging.debug("Loaded weight: %s" % weights)

''' Call word split routing and update globals with output. '''
split_word(args.word)

logging.debug("------------------------")
logging.debug("Printing Split: \n%s" % split)
logging.debug("Printing Index: \n%s" % index)
logging.debug("Printing no of splits: \n%s" % no_of_splits)
logging.debug("Printing rules applied: \n%s" % rule_applied)
logging.debug("------------------------")

''' Does further split of rules and words and queries morpholigical place and writes result in a result file '''
split_final()
''' Output of result file is matching in b/w Python and CPP code with only order difference. '''

logging.debug("New splits are: %s" % new_splits)
logging.debug("Size of new splits is: %d" % len(new_splits))
logging.debug("New rules applied are: %s" % new_rule_applied)
logging.debug("Value loaded in os is: %s" % op)

# Many of the code snippets are just translated, not optimized
            
calculate_costs()

logging.debug('Total cost (tot_cost) :\n %s' % tot_cost)
logging.debug('Cost (costs) :\n %s' % costs)
logging.debug('Output1 (output1) :\n %s' % output1)

logging.debug('Final_cost before sorting :\n %s' % final_costs)
final_costs.sort(reverse = True)
logging.debug('Final cost after sorting :\n %s' % final_costs)
count = 0
fount = 0
correct_ones = 0
for each in range(0, len(final_costs)):
   temp1 = output1[final_costs[each]] 
   count = each + 1
   logging.debug(temp1[0])
   word = "+".join(temp1[0])
   logging.debug(args.switch)
   if args.switch == "testing" and (count == 1):
       print("%s = %s\t%s" % (args.word, word, final_costs[each]))
       found = 1
   elif args.switch == "compare" and (word == 'sandhi'):
       correct_ones += 1
       print("\nThe expected split for : " + args.word)
       print("%s\t %s\t %s" % (word, final_costs[i], count))
       found = 1
       # Put ranks logic
       # ranks[count]=ranks[count]+1;

# Not porting further as it seems all is for -C option, which is not used.
