'''
@author David Glover
CS 4013 - Compiler Construction
Project 1 - Lexical Analyzer
September 26, 2014
'''

from lexical_analyzer import *
import sys
import os

def main_proj1():
    src_file = open(os.path.abspath('../Data/src_program'), 'r')
    listing_file = open(os.path.abspath('../Data/listing_file'), 'w')
    token_file = open(os.path.abspath('../Data/token_file'), 'w')
    symbol_file = open(os.path.abspath('../Data/symbol_file'), 'w')
    Lexical_Analyzer(src_file, listing_file, token_file, symbol_file)

if __name__ == '__main__':
	main_proj1()