'''
@author David Glover
CS 4013 - Compiler Construction
Project 2 - Syntax Analysis
November 13, 2014
'''

class Recursive_Descent:
	def __init__(self, t_list, listing_file_list, listing_file):
		global token_list, token, l_file_lines
		token_list = t_list
		token = token_list.pop(0)
		l_file_lines = listing_file_list
		self.program()
		self.match('$')
		for line in l_file_lines:
			listing_file.write(line)
		listing_file.close()

	def match(self, t):
		global token_list, token
		i = 0
		try:
			while i < len(t) and int(t[i]) != token.token_type:
				i += 1
			if i < len(t) and token.token_type == int(t[i]) and token_list:
				token = token_list.pop(0)
			else:
				self.add_error(token.line_number, t, 0)
				if token_list: token = token_list.pop(0)
		except:
			while i < len(t) and str(t[i]) != token.lexeme:
				i += 1
			if i < len(t) and token.lexeme == str(t[i]):
				if t[i] != '$' and token_list:
					token = token_list.pop(0)
				else:
					print('Parse complete.')
			else:
				self.add_error(token.line_number, t, 0)
				if token_list: token = token_list.pop(0)

	def synch(self, synch_set, firsts):
		global token, token_list
		self.add_error(token.line_number, firsts, 0)
		i = 0
		try:
			while token.token_type not in synch_set and token_list:
				token = token_list.pop(0)
		except:
			while token.lexeme not in synch_set and token_list:
				token = token_list.pop(0)
		if not token_list:
			self.add_error(token.line_number, token.lexeme, 1)

	def add_error(self, line_num, exp, err_type):
		global l_file_lines, token
		j = 0
		while len(l_file_lines[j]) > 0 and ' '.join(l_file_lines[j].split()[:1]) != str(line_num):
			j += 1
		while len(l_file_lines[j]) > 0 and j < len(l_file_lines) - 1 and (' '.join(l_file_lines[j].split()[:1]) in ['LEXERR:', 'SYNERR:', 'No'] or ' '.join(l_file_lines[j + 1].split()[:1]) in ['LEXERR:', 'Syntax', 'No']) and ' '.join(l_file_lines[j + 1].split()[:1]) != str(line_num + 1):
			j += 1
		if err_type == 0:
			l_file_lines.insert(j + 1, 'SYNERR: Expected ' + ', '.join(exp) + '; Received ' + token.lexeme + '\n')
		elif err_type == 1:
			l_file_lines.insert(j + 1, 'No more tokens available. Synch failed while looking for ' + token.lexeme + '\n')

	def program(self):
		global token
		if token.lexeme == 'program':
			self.match(['program'])
			self.match([1])
			self.match(['('])
			self.identifier_list()
			self.match([')'])
			self.match([';'])
			self.program2()
		else:
			self.synch(['$', 'program'], ['program'])
		
	def program2(self):
		global token
		if token.lexeme == 'begin':
			self.compound_statement()
			self.match(['.'])
		elif token.lexeme == 'procedure':
			self.subprogram_declarations()
			self.compound_statement()
			self.match(['.'])
		elif token.lexeme == 'var':
			self.declarations()
			self.program3()
		else:
			self.synch(['$', 'begin', 'procedure', 'var'], ['begin', 'procedure', 'var'])
		
	def program3(self):
		global token
		if token.lexeme == 'begin':
			self.compound_statement()
			self.match(['.'])
		elif token.lexeme == 'procedure':
			self.subprogram_declarations()
			self.compound_statement()
			self.match(['.'])
		else:
			self.synch(['$', 'begin', 'procedure'], ['begin', 'procedure'])
		
	def identifier_list(self):
		global token
		if token.token_type == 1:
			self.match([1])
			self.identifier_list2()
		else:
			self.synch(['$', 1, ')'], ['id'])
		
	def identifier_list2(self):
		global token
		if token.lexeme == ',':
			self.match([','])
			self.match([1])
			self.identifier_list2()
		elif token.lexeme != ')':
			self.synch(['$', ',', ')'], [','])
		
	def declarations(self):
		global token
		if token.lexeme == 'var':
			self.match(['var'])
			self.match([1])
			self.match([':'])
			self.type()
			self.match([';'])
			self.declarations2()
		else:
			self.synch(['$', 'var', 'begin', 'procedure'], ['var'])
		
	def declarations2(self):
		global token
		if token.lexeme == 'var':
			self.match(['var'])
			self.match([1])
			self.match([':'])
			self.type()
			self.match([';'])
			self.declarations2()
		elif token.lexeme not in ['procedure', 'begin']:
			self.synch(['$', 'var', 'begin', 'procedure'], ['var'])
		
	def type(self):
		global token
		if token.lexeme in ['integer', 'real']:
			self.standard_type()
		elif token.lexeme == 'array':
			self.match(['array'])
			self.match(['['])
			self.match([32, 33, 34])
			self.match(['..'])
			self.match([32, 33, 34])
			self.match([']'])
			self.match(['of'])
			self.standard_type()
		else:
			self.synch(['$', 'integer', 'real', 'array', ';', ')'], ['integer', 'real', 'array'])
		
	def standard_type(self):
		global token
		if token.lexeme == 'integer':
			self.match(['integer'])
		elif token.lexeme == 'real':
			self.match(['real'])
		else:
			self.synch(['$', 'integer', 'real', ';', ')'], ['integer', 'real'])
		
	def subprogram_declarations(self):
		global token
		if token.lexeme == 'procedure':
			self.subprogram_declaration()
			self.match([';'])
			self.subprogram_declarations2()
		else:
			self.synch(['$', 'procedure', 'begin'], ['procedure'])
		
	def subprogram_declarations2(self):
		global token
		if token.lexeme == 'procedure':
			self.subprogram_declaration()
			self.match([';'])
			self.subprogram_declarations2()
		elif token.lexeme != 'begin':
			self.synch(['$', 'procedure', 'begin'], ['procedure'])
		
	def subprogram_declaration(self):
		global token
		if token.lexeme == 'procedure':
			self.subprogram_head()
			self.subprogram_declaration2()
		else:
			self.synch(['$', 'procedure', ';'], ['procedure'])
		
	def subprogram_declaration2(self):
		global token
		if token.lexeme == 'var':
			self.declarations()
			self.subprogram_declaration3()
		elif token.lexeme == 'begin':
			self.compound_statement()
		elif token.lexeme == 'procedure':
			self.subprogram_declarations()
			self.compound_statement()
		else:
			self.synch(['$', 'var', 'begin', 'procedure', ';'], ['var', 'begin', 'procedure'])
		
	def subprogram_declaration3(self):
		global token
		if token.lexeme == 'begin':
			self.compound_statement()
		elif token.lexeme == 'procedure':
			self.subprogram_declarations()
			self.compound_statement()
		else:
			self.synch(['$', 'begin', 'procedure', ';'], ['begin', 'procedure'])
		
	def subprogram_head(self):
		global token
		if token.lexeme == 'procedure':
			self.match(['procedure'])
			self.match([1])
			self.subprogram_head2()
		else:
			self.synch(['$', 'procedure', 'var', 'begin'], ['procedure'])
		
	def subprogram_head2(self):
		global token
		if token.lexeme == '(':
			self.arguments()
			self.match([';'])
		elif token.lexeme == ';':
			self.match([';'])
		else:
			self.synch(['$', '(', ';', 'var', 'begin', 'procedure'], ['(', ';'])
		
	def arguments(self):
		global token
		if token.lexeme == '(':
			self.match(['('])
			self.parameter_list()
			self.match([')'])
		else:
			self.synch(['$', '(', ';'], ['('])
		
	def parameter_list(self):
		global token
		if token.token_type == 1:
			self.match([1])
			self.match([':'])
			self.type()
			self.parameter_list2()
		else:
			self.synch(['$', 1, ')'], ['id'])
		
	def parameter_list2(self):
		global token
		if token.lexeme == ';':
			self.match([';'])
			self.match([1])
			self.match([':'])
			self.type()
			self.parameter_list2()
		elif token.lexeme != ')':
			self.synch(['$', ';', ')'], [';'])
		
	def compound_statement(self):
		global token
		if token.lexeme == 'begin':
			self.match(['begin'])
			self.compound_statement2()
		else:
			self.synch(['$', 'begin', '.', 'else', ';', 'end'], ['begin'])
		
	def compound_statement2(self):
		global token
		if token.token_type == 1 or token.lexeme in ['begin', 'if', 'while', 'call']:
			self.statement_list()
			self.match(['end'])
		elif token.lexeme == 'end':
			self.match(['end'])
		else:
			self.synch(['$', 1, 'call', 'begin', 'if', 'while', 'end', '.', 'else', ';'], ['id', 'begin', 'if', 'while', 'call'])
		
	def statement_list(self):
		global token
		if token.token_type == 1 or token.lexeme in ['begin', 'if', 'while', 'call']:
			self.statement()
			self.statement_list2()
		else:
			self.synch(['$', 1, 'call', 'begin', 'if', 'while', 'end'], ['id', 'begin', 'if', 'while', 'call'])
		
	def statement_list2(self):
		global token
		if token.lexeme == ';':
			self.match([';'])
			self.statement()
			self.statement_list2()
		elif token.lexeme != 'end':
			self.synch(['$', ';', 'end'], [';'])
		
	def statement(self):
		global token
		if token.token_type == 1:
			self.variable()
			self.match([30])
			self.expression()
		elif token.lexeme == 'call':
			self.procedure_statement()
		elif token.lexeme == 'begin':
			self.compound_statement()
		elif token.lexeme == 'if':
			self.match(['if'])
			self.expression()
			self.match(['then'])
			self.statement()
			self.statement2()
		elif token.lexeme == 'while':
			self.match(['while'])
			self.expression()
			self.match(['do'])
			self.statement()
		else:
			self.synch(['$', 1, 'call', 'begin', 'if', 'while', 'else', ';', 'end'], ['id', 'call', 'begin', 'if', 'while'])
		
	def statement2(self):
		global token
		if token.lexeme == 'else':
			self.match(['else'])
			self.statement()
		elif token.lexeme not in [';', 'end']:
			self.synch(['$', 'else', ';', 'end'], ['else'])
		
	def variable(self):
		global token
		if token.token_type == 1:
			self.match([1])
			self.variable2()
		else:
			self.synch(['$', 1, 30], ['id'])
		
	def variable2(self):
		global token
		if token.lexeme == '[':
			self.match(['['])
			self.expression()
			self.match([']'])
		elif token.token_type != 30:
			self.synch(['$', '[', 30], ['['])
		
	def procedure_statement(self):
		global token
		if token.lexeme == 'call':
			self.match(['call'])
			self.match([1])
			self.procedure_statement2()
		else:
			self.synch(['$', 'call', 'else', ';', 'end'], ['call'])
		
	def procedure_statement2(self):
		global token
		if token.lexeme == '(':
			self.match(['('])
			self.expression_list()
			self.match(')')
		elif token.lexeme not in [';', 'end', 'else']:
			self.synch(['$', '(', 'else', ';', 'end'], ['('])
		
	def expression_list(self):
		global token
		if token.token_type in [1, 32, 33, 34] or token.lexeme in ['not', '+', '-', '(']:
			self.expression()
			self.expression_list2()
		else:
			self.synch(['$', 1, 32, 33, 34, '(', 'not', '+', '-', ')'], ['id', 'num', 'not', '+', '-', '('])
		
	def expression_list2(self):
		global token
		if token.lexeme == ',':
			self.match([','])
			self.expression()
			self.expression_list2()
		elif token.lexeme != ')':
			self.synch(['$', ',', ')'], [','])

	def expression(self):
		global token
		if token.token_type in [1, 32, 33, 34] or token.lexeme in ['not', '+', '-', '(']:
			self.simple_expression()
			self.expression2()
		else:
			self.synch(['$', 1, 32, 33, 34, '(', 'not', '+', '-', ']', ')', ',', 'then', 'do', 'else', ';', 'end'], ['id', 'num', 'not', '+', '-', '('])
		
	def expression2(self):
		global token
		if token.token_type == 2:
			self.match([2])
			self.simple_expression()
		elif token.lexeme not in ['end', 'then', 'else', 'do', ')', ']', ',', ';']:
			self.synch(['$', 2, ']', ')', ',', 'then', 'do', 'else', ';', 'end'], ['relop'])
		
	def simple_expression(self):
		global token
		if token.token_type in [1, 32, 33, 34] or token.lexeme in ['not', '(']:
			self.term()
			self.simple_expression2()
		elif token.lexeme in ['+', '-']:
			self.sign()
			self.term()
			self.simple_expression2()
		else:
			self.synch(['$', 1, 32, 33, 34, '(', 'not', '+', '-', 2, ']', ')', ',', 'then', 'do', 'else', ';', 'end'], ['id', 'num', 'not', '(', '+', '-'])
		
	def simple_expression2(self):
		global token
		if token.token_type == 4:
			self.match([4])
			self.term()
			self.simple_expression2()
		elif token.token_type != 2 and token.lexeme not in ['end', 'then', 'else', 'do', ')', ']', ',', ';']:
			self.synch(['$', 4, 2, ']', ')', ',', 'then', 'do', 'else', ';', 'end'], ['addop'])
		
	def term(self):
		global token
		if token.token_type in [1, 32, 33, 34] or token.lexeme in ['not', '(']:
			self.factor()
			self.term2()
		else:
			self.synch(['$', 1, 32, 33, 34, '(', 'not', 4, 2, ']', ')', ',', 'then', 'do', 'else', ';', 'end'], ['id', 'num', 'not', '('])
		
	def term2(self):
		global token
		if token.token_type == 3:
			self.match([3])
			self.factor()
			self.term2()
		elif token.token_type not in [2, 4] and token.lexeme not in ['end', 'then', 'else', 'do', ')', ']', ',', ';']:
			self.synch(['$', 3, 4, 2, ']', ')', ',', 'then', 'do', 'else', ';', 'end'], ['mulop'])
		
	def factor(self):
		global token
		if token.token_type == 1:
			self.match([1])
			self.factor2()
		elif token.token_type in [32, 33, 34]:
			self.match([32, 33, 34])
		elif token.lexeme == '(':
			self.match(['('])
			self.expression()
			self.match([')'])
		elif token.lexeme == 'not':
			self.match(['not'])
			self.factor()
		else:
			self.synch(['$', 1, 32, 33, 34, '(', 'not', 3, 4, 2, ']', ')', ',', 'then', 'do', 'else', ';', 'end'], ['id', 'num', '(', 'not'])
		
	def factor2(self):
		global token
		if token.lexeme == '[':
			self.match(['['])
			self.expression()
			self.match([']'])
		elif token.token_type not in [2, 3, 4] and token.lexeme not in ['end', 'then', 'else', 'do', ')', ']', ',', ';']:
			self.synch(['$', '[', 3, 4, 2, ']', ')', ',', 'then', 'do', 'else', ';', 'end'], ['['])

	def sign(self):
		global token
		if token.lexeme == '+':
			self.match(['+'])
		elif token.lexeme == '-':
			self.match(['-'])
		else:
			self.synch(['$', '+', '-', 1, 32, 33, 34, '(', 'not'], ['+', '-'])