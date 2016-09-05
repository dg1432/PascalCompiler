'''
@author David Glover
CS 4013 - Compiler Construction
Project 1 - Lexical Analyzer
September 26, 2014
'''

class Token:
    def __init__(self, lexeme, token_type, token, attribute_type, attribute):
        self.lexeme = lexeme
        self.token_type = token_type
        self.token = token
        self.attribute_type = attribute_type
        self.attribute = attribute