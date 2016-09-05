'''
@author David Glover
CS 4013 - Compiler Construction
Project 2 - Syntax Analysis
November 13, 2014
'''

from recursive_descent import *
from lexical_analyzer import *
import os

def main_proj2():
    src_file = open(os.path.abspath('../Data/src_program'), 'r')
    listing_file = open(os.path.abspath('../Data/listing_file'), 'w')
    token_file = open(os.path.abspath('../Data/token_file'), 'w')
    symbol_file = open(os.path.abspath('../Data/symbol_file'), 'w')
    Lexical_Analyzer(src_file, listing_file, token_file, symbol_file)

if __name__ == '__main__':
	main_proj2()