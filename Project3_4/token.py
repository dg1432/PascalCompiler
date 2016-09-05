'''
@author David Glover
CS 4013 - Compiler Construction
Project 3 and 4 - Type and Scope Checking and
                  Memory Address Computations
January 15, 2015
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