'''
@author David Glover
CS 4013 - Compiler Construction
Project 3 and 4 - Type and Scope Checking and
                  Memory Address Computations
January 15, 2015
'''

class Type_Wrapper():
	def __init__(self, t, synth, v, s):
		self.type = t
		self.synthesized = synth
		self.value = v
		self.size = s