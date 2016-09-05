'''
@author David Glover
CS 4013 - Compiler Construction
Project 2 - Syntax Analyzer
November 13, 2014
'''

class Token:
    def __init__(self, l_n, l, t_t, t, a_t, a):
    	self.line_number = l_n
        self.lexeme = l
        self.token_type = t_t
        self.token = t
        self.attribute_type = a_t
        self.attribute = a

class TokenRD:
	def __init__(self, l_n, l, t_t, a):
		self.line_number = l_n
		self.lexeme = l
		self.token_type = t_t
		self.attribute = a