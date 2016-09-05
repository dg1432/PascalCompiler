'''
@author David Glover
CS 4013 - Compiler Construction
Project 3 and 4 - Type and Scope Checking and
                  Memory Address Computations
January 15, 2015
'''

from lexical_analyzer import *
import os

def main_proj3_4():
    src_file = open(os.path.abspath('../Data/src_program'), 'r')
    listing_file = open(os.path.abspath('../Data/listing_file'), 'w')
    token_file = open(os.path.abspath('../Data/token_file'), 'w')
    symbol_file = open(os.path.abspath('../Data/symbol_file'), 'w')
    memory_file = open(os.path.abspath('../Data/mem_addresses'), 'w')
    Lexical_Analyzer(src_file, listing_file, token_file, symbol_file, memory_file)

if __name__ == '__main__':
	main_proj3_4()