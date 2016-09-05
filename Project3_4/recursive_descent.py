'''
@author David Glover
CS 4013 - Compiler Construction
Project 3 and 4 - Type and Scope Checking and
                  Memory Address Computations
January 15, 2015
'''

from type_wrapper import *
from node import *

class Recursive_Descent:
	def __init__(self, t_list, listing_file_list, listing_file, symbol_list, symbol_file, memory_file):
		global token_list, token, l_file_lines, s_file_lines, s_file_lines_types, scope_tree, green_node_stack, m_file_lines
		token_list = t_list
		token = token_list.pop(0)
		l_file_lines = listing_file_list
		s_file_lines = symbol_list
		s_file_lines_types = []
		m_file_lines = []
		scope_tree = Node_Tree()
		green_node_stack = []
		if token_list: self.program()
		self.match('$')
		for line in l_file_lines:
			listing_file.write(line)
		listing_file.close()
		tabs = '\t\t\t'
		symbol_file.write('Name\t\tAddress\t\t\tType\n')
		for line in s_file_lines_types:
			symbol_file.write(str(line[0]) + tabs[0:len(tabs) - len(str(line[0])) / 4] + str(line[1]) + '\t\t' + str(line[2]) + '\n')
		symbol_file.close()
		memory_file.write('Name\t\tAddress\n')
		for line in m_file_lines:
			memory_file.write(str(line[0] + tabs[0:len(tabs) - len(str(line[0])) / 4] + str(line[1]) + '\n'))
		memory_file.close()

	def match(self, t):
		global token_list, token
		i = 0
		try:
			while i < len(t) and int(t[i]) != token.token_type:
				i += 1
			if i < len(t) and token.token_type == int(t[i]) and token_list:
				token = token_list.pop(0)
			else:
				if t == [1]: t = ['id']
				elif t == [2]: t = ['relop']
				elif t == [3]: t = ['mulop']
				elif t == [4]: t = ['addop']
				self.add_error(token.line_number, t, 0)
				if token_list: token = token_list.pop(0)
		except:
			while i < len(t) and str(t[i]) != token.lexeme:
				i += 1
			if i < len(t) and token.lexeme == str(t[i]):
				if t[i] != '$' and token_list:
					token = token_list.pop(0)
			else:
				self.add_error(token.line_number, t, 0)
				if token_list: token = token_list.pop(0)

	def synch(self, synch_set, firsts):
		global token, token_list
		self.add_error(token.line_number, firsts, 0)
		while token.token_type not in synch_set and token.lexeme not in synch_set and token_list:
			token = token_list.pop(0)
		if not token_list:
			self.add_error(token.line_number, token.lexeme, 'id')

	def add_error(self, line_num, exp, err_type, err_msg = None):
		global l_file_lines, token
		j = 0
		while len(l_file_lines[j]) > 0 and ' '.join(l_file_lines[j].split()[:1]) != str(line_num):
			j += 1
		while len(l_file_lines[j]) > 0 and j < len(l_file_lines) - 1 and (' '.join(l_file_lines[j].split()[:1]) in ['LEXERR:', 'SYNERR:', 'SEMERR:', 'No'] or ' '.join(l_file_lines[j + 1].split()[:1]) in ['LEXERR:', 'SYNERR:', 'SEMERR:', 'No']) and ' '.join(l_file_lines[j + 1].split()[:1]) != str(line_num + 1):
			j += 1
		if err_type == 0:
			l_file_lines.insert(j + 1, 'SYNERR: Expected ' + ', '.join(str(e) for e in exp) + '; Received ' + token.lexeme + '\n')
		elif err_type == 1:
			l_file_lines.insert(j + 1, 'No more tokens available. Synch failed while looking for ' + token.lexeme + '\n')
		elif err_type == 2:
			l_file_lines.insert(j + 1, 'SEMERR: ' + err_msg + '\n')

	def add_type(self, p_id, p_type):
		global s_file_lines, s_file_lines_types
		i = 0
		while i < len(s_file_lines) and p_id.lexeme != s_file_lines[i][0]:
			i += 1
		if s_file_lines and i < len(s_file_lines) and p_id.lexeme == s_file_lines[i][0]:
			for s in s_file_lines_types:
				if p_id.lexeme == s[0]:
					return
			s_file_lines_types.append([p_id.lexeme, s_file_lines[i][1], p_type])

	def get_num_params(self, node):
		tmp = []
		for n in node.blue_nodes:
			if n.type[:2] == 'PP':
				tmp.append(node)
		return len(tmp)

	def get_pointer(self, search_node, l_n):
		global green_node_stack, scope_tree
		scope = []
		scope.append(green_node_stack[0])
		for c in scope_tree.search(green_node_stack).children:
			scope.append(c)
		for a in green_node_stack[1:]:
			scope.append(a)
		if search_node.color == 'blue':
			for node in scope:
				for b in node.blue_nodes:
					if search_node.name == b.name and search_node.color == b.color:
						return b
		else:
			if len(green_node_stack) > 1:
				for s in scope_tree.search(green_node_stack[1:]).children:
					scope.append(s)
			for node in scope:
				if node.name == search_node.name:
					return node
		tmp = []
		for g in green_node_stack: tmp.append(g.name)
		if (search_node.color == 'blue' and search_node.name not in tmp) or search_node.color == 'green':
			self.add_error(l_n, None, 2, search_node.name + ' was not declared or is outside the current scope.')
		return None

	def push_green_node(self, node, l_n):
		global green_node_stack
		if node in green_node_stack:
			self.add_error(l_n, None, 2, node.name + ' has already been declared in this scope.')
		green_node_stack.insert(0, node)

	def push_blue_node(self, s_node, node, l_n):
		global green_node_stack
		for b in green_node_stack[0].blue_nodes:
			if node.name == b.name and node.color == b.color:
				self.add_error(l_n, None, 2, node.name + ' has already been declared in the local scope.')
				break
		s_node.blue_nodes.append(node)

	def program(self):
		global token, offset, scope_tree, green_node_stack, m_file_lines
		program_w = Type_Wrapper(None, None, None, 0)
		if token.lexeme == 'program':
			self.match(['program'])
			p_id = token
			self.match([1])
			self.add_type(p_id, 'PGNAME')
			offset = 0
			m_file_lines.append([p_id.lexeme, 'FFFFFFFF'])
			node = Node('green', p_id.lexeme, 'PGNAME')
			scope_tree.insert_node(node, green_node_stack)
			self.push_green_node(node, p_id.line_number)
			self.match(['('])
			il_w = self.identifier_list(self.get_pointer(Node('green', p_id.lexeme, 'PGNAME'), p_id.line_number))
			self.match([')'])
			self.match([';'])
			self.program2(il_w.synthesized)
			green_node_stack.pop(0)
		else:
			self.synch(['$', 'program'], ['program'])
		return program_w
		
	def program2(self, inherited):
		global token
		program2_w = Type_Wrapper(None, None, None, 0)
		if token.lexeme == 'begin':
			self.compound_statement()
			self.match(['.'])
		elif token.lexeme == 'procedure':
			self.subprogram_declarations(inherited)
			self.compound_statement()
			self.match(['.'])
		elif token.lexeme == 'var':
			d_w = self.declarations(inherited)
			self.program3(d_w.synthesized)
		else:
			self.synch(['$', 'begin', 'procedure', 'var'], ['begin', 'procedure', 'var'])
		return program2_w
		
	def program3(self, inherited):
		global token
		program3_w = Type_Wrapper(None, None, None, 0)
		if token.lexeme == 'begin':
			self.compound_statement()
			self.match(['.'])
		elif token.lexeme == 'procedure':
			self.subprogram_declarations(inherited)
			self.compound_statement()
			self.match(['.'])
		else:
			self.synch(['$', 'begin', 'procedure'], ['begin', 'procedure'])
		return program3_w
		
	def identifier_list(self, inherited):
		global token, scope_tree, green_node_stack, m_file_lines
		identifier_list_w = Type_Wrapper(None, None, None, 0)
		if token.token_type == 1:
			p_id = token
			self.add_type(p_id, 'PGPARM')
			self.match([1])
			m_file_lines.append([p_id.lexeme, 'FFFFFFFF'])
			if inherited:
				node = scope_tree.search(green_node_stack)
				self.push_blue_node(node, Node('blue', p_id.lexeme, 'PGPARM'), p_id.line_number)
				il2_w = self.identifier_list2(self.get_pointer(Node('blue', p_id.lexeme, 'PGPARM'), p_id.line_number))
			else:
				il2_w = self.identifier_list2(inherited)
			identifier_list_w.synthesized = il2_w.synthesized
		else:
			self.synch(['$', 1, ')'], ['id'])
		return identifier_list_w
		
	def identifier_list2(self, inherited):
		global token, scope_tree, green_node_stack, m_file_lines
		identifier_list2_w = Type_Wrapper(None, None, None, 0)
		if token.lexeme == ',':
			self.match([','])
			p_id = token
			self.add_type(p_id, 'PGPARM')
			self.match([1])
			m_file_lines.append([p_id.lexeme, 'FFFFFFFF'])
			if inherited:
				node = scope_tree.search(green_node_stack)
				self.push_blue_node(node, Node('blue', p_id.lexeme, 'PGPARM'), p_id.line_number)
				il2_w = self.identifier_list2(self.get_pointer(Node('blue', p_id.lexeme, 'PGPARM'), p_id.line_number))
			else:
				il2_w = self.identifier_list2(inherited)
			identifier_list2_w.synthesized = il2_w.synthesized
		elif token.lexeme == ')':
			identifier_list2_w.synthesized = inherited
		else:
			self.synch(['$', ',', ')'], [','])
		return identifier_list2_w
		
	def declarations(self, inherited):
		global token, offset, m_file_lines
		declarations_w = Type_Wrapper(None, None, None, 0)
		if token.lexeme == 'var':
			self.match(['var'])
			p_id = token
			self.match([1])
			self.match([':'])
			t_w = self.type()
			self.match([';'])
			m_file_lines.append([p_id.lexeme, offset])
			offset += t_w.size
			self.add_type(p_id, t_w.type)
			if inherited:
				node = scope_tree.search(green_node_stack)
				self.push_blue_node(node, Node('blue', p_id.lexeme, t_w.type), p_id.line_number)
				d2_w = self.declarations2(self.get_pointer(Node('blue', p_id.lexeme, t_w.type), p_id.line_number))
			else:
				node = scope_tree.search(green_node_stack)
				self.push_blue_node(node, Node('blue', p_id.lexeme, t_w.type), p_id.line_number)
				d2_w = self.declarations2(inherited)
			declarations_w.synthesized = d2_w.synthesized
		else:
			self.synch(['$', 'var', 'begin', 'procedure'], ['var'])
		return declarations_w
		
	def declarations2(self, inherited):
		global token, offset, m_file_lines
		declarations2_w = Type_Wrapper(None, None, None, 0)
		if token.lexeme == 'var':
			self.match(['var'])
			p_id = token
			self.match([1])
			self.match([':'])
			t_w = self.type()
			self.match([';'])
			m_file_lines.append([p_id.lexeme, offset])
			offset += t_w.size
			self.add_type(p_id, t_w.type)
			node = scope_tree.search(green_node_stack)
			self.push_blue_node(node, Node('blue', p_id.lexeme, t_w.type), p_id.line_number)
			d2_w = self.declarations2(self.get_pointer(Node('blue', p_id.lexeme, t_w.type), p_id.line_number))
			declarations2_w.synthesized = d2_w.synthesized
		elif token.lexeme in ['procedure', 'begin']:
			declarations2_w.synthesized = inherited
		else:
			self.synch(['$', 'var', 'begin', 'procedure'], ['var'])
		return declarations2_w
		
	def type(self):
		global token
		type_w = Type_Wrapper(None, None, None, 0)
		if token.lexeme in ['integer', 'real']:
			st_w = self.standard_type()
			type_w.type = st_w.type
			type_w.size = st_w.size
		elif token.lexeme == 'array':
			self.match(['array'])
			self.match(['['])
			num1 = token
			self.match([32, 33, 34])
			self.match(['..'])
			num2 = token
			self.match([32, 33, 34])
			rbrack = token
			self.match([']'])
			self.match(['of'])
			st_w = self.standard_type()
			try:
				if int(num1.lexeme) > int(num2.lexeme):
					type_w.type = 'ERR*'
					type_w.size = 0
					self.add_error(rbrack.line_number, None, 2, 'Invalid array range.')
				else:
					if st_w.type in ['INT', 'REAL']:
						type_w.type = 'A' + st_w.type
					type_w.size = (int(num2.lexeme) - int(num1.lexeme) + 1) * int(st_w.size)
			except:
				type_w.type = 'ERR*'
				type_w.size = 0
				self.add_error(num2.line_number, None, 2, 'Array indices must both be numerical integers.')
		else:
			self.synch(['$', 'integer', 'real', 'array', ';', ')'], ['integer', 'real', 'array'])
		return type_w
		
	def standard_type(self):
		global token
		standard_type_w = Type_Wrapper(None, None, None, 0)
		if token.lexeme == 'integer':
			self.match(['integer'])
			standard_type_w.type = 'INT'
			standard_type_w.size = 4
		elif token.lexeme == 'real':
			self.match(['real'])
			standard_type_w.type = 'REAL'
			standard_type_w.size = 8
		else:
			self.synch(['$', 'integer', 'real', ';', ')'], ['integer', 'real'])
		return standard_type_w
		
	def subprogram_declarations(self, inherited):
		global token
		subprogram_declarations_w = Type_Wrapper(None, None, None, 0)
		if token.lexeme == 'procedure':
			sd_w = self.subprogram_declaration(inherited)
			self.match([';'])
			sd2_w = self.subprogram_declarations2(sd_w.synthesized)
			subprogram_declarations_w.synthesized = sd2_w.synthesized
		else:
			self.synch(['$', 'procedure', 'begin'], ['procedure'])
		return subprogram_declarations_w
		
	def subprogram_declarations2(self, inherited):
		global token
		subprogram_declarations2_w = Type_Wrapper(None, None, None, 0)
		if token.lexeme == 'procedure':
			sd_w = self.subprogram_declaration(inherited)
			self.match([';'])
			sd2_w = self.subprogram_declarations2(sd_w.synthesized)
			subprogram_declarations2_w.synthesized = sd2_w.synthesized
		elif token.lexeme != 'begin':
			self.synch(['$', 'procedure', 'begin'], ['procedure'])
		return subprogram_declarations2_w
		
	def subprogram_declaration(self, inherited):
		global token, green_node_stack
		subprogram_declaration_w = Type_Wrapper(None, None, None, 0)
		if token.lexeme == 'procedure':
			sh_w = self.subprogram_head(inherited)
			sd2_w = self.subprogram_declaration2(sh_w.synthesized)
			green_node_stack.pop(0)
			subprogram_declaration_w.synthesized = sd2_w.synthesized
		else:
			self.synch(['$', 'procedure', ';'], ['procedure'])
		return subprogram_declaration_w
		
	def subprogram_declaration2(self, inherited):
		global token
		subprogram_declaration2_w = Type_Wrapper(None, None, None, 0)
		if token.lexeme == 'var':
			d_w = self.declarations(inherited)
			sd3_w = self.subprogram_declaration3(d_w.synthesized)
			subprogram_declaration2_w.synthesized = sd3_w.synthesized
		elif token.lexeme == 'begin':
			self.compound_statement()
			subprogram_declaration2_w.synthesized = inherited
		elif token.lexeme == 'procedure':
			sd_w = self.subprogram_declarations(inherited)
			self.compound_statement()
			subprogram_declaration2_w.synthesized = sd_w.synthesized
		else:
			self.synch(['$', 'var', 'begin', 'procedure', ';'], ['var', 'begin', 'procedure'])
		return subprogram_declaration2_w
		
	def subprogram_declaration3(self, inherited):
		global token
		subprogram_declaration3_w = Type_Wrapper(None, None, None, 0)
		if token.lexeme == 'begin':
			self.compound_statement()
			subprogram_declaration3_w.synthesized = inherited
		elif token.lexeme == 'procedure':
			sd_w = self.subprogram_declarations(inherited)
			self.compound_statement()
			subprogram_declaration3_w.synthesized = sd_w.synthesized
		else:
			self.synch(['$', 'begin', 'procedure', ';'], ['begin', 'procedure'])
		return subprogram_declaration3_w
		
	def subprogram_head(self, inherited):
		global token, offset, m_file_lines
		subprogram_head_w = Type_Wrapper(None, None, None, 0)
		if token.lexeme == 'procedure':
			self.match(['procedure'])
			p_id = token
			self.add_type(p_id, 'PROC')
			self.match([1])
			m_file_lines.append([p_id.lexeme, 'FFFFFFFF'])
			offset = 0
			new_node = Node('green', p_id.lexeme, 'PROC')
			scope_tree.insert_node(new_node, green_node_stack)
			self.push_green_node(new_node, p_id.line_number)
			if inherited:
				sh2_w = self.subprogram_head2(self.get_pointer(Node('green', p_id.lexeme, 'PROC'), p_id.line_number))
			else:
				sh2_w = self.subprogram_head2(None)
			subprogram_head_w.synthesized = inherited
		else:
			self.synch(['$', 'procedure', 'var', 'begin'], ['procedure'])
		return subprogram_head_w
		
	def subprogram_head2(self, inherited):
		global token, green_node_stack
		subprogram_head2_w = Type_Wrapper(None, None, None, 0)
		if token.lexeme == '(':
			a_w = self.arguments(inherited)
			self.match([';'])
			subprogram_head2_w.synthesized = a_w.synthesized
		elif token.lexeme == ';':
			self.match([';'])
			subprogram_head2_w.synthesized = inherited
		else:
			self.synch(['$', '(', ';', 'var', 'begin', 'procedure'], ['(', ';'])
		return subprogram_head2_w
		
	def arguments(self, inherited):
		global token
		arguments_w = Type_Wrapper(None, None, None, 0)
		if token.lexeme == '(':
			self.match(['('])
			pl_w = self.parameter_list(inherited)
			self.match([')'])
			arguments_w.synthesized = pl_w.synthesized
		else:
			self.synch(['$', '(', ';'], ['('])
		return arguments_w
		
	def parameter_list(self, inherited):
		global token, green_node_stack, m_file_lines
		parameter_list_w = Type_Wrapper(None, None, None, 0)
		if token.token_type == 1:
			p_id = token
			self.match([1])
			self.match([':'])
			t_w = self.type()
			m_file_lines.append([p_id.lexeme, 'FFFFFFFF'])
			if t_w.type in ['INT', 'REAL', 'AINT', 'AREAL']:
				t_w.type = 'PP' + t_w.type
				node = scope_tree.search(green_node_stack)
				self.push_blue_node(node, Node('blue', p_id.lexeme, t_w.type), p_id.line_number)
			else:
				t_w.type = 'ERR'
				node = scope_tree.search(green_node_stack)
				self.push_blue_node(node, Node('blue', p_id.lexeme, 'ERR'), p_id.line_number)
			self.add_type(p_id, t_w.type)
			pl2_w = self.parameter_list2([node.name])
			parameter_list_w.synthesized = pl2_w.synthesized
		else:
			self.synch(['$', 1, ')'], ['id'])
		return parameter_list_w
		
	def parameter_list2(self, inherited):
		global token
		parameter_list2_w = Type_Wrapper(None, None, None, 0)
		if token.lexeme == ';':
			self.match([';'])
			p_id = token
			self.match([1])
			self.match([':'])
			t_w = self.type()
			m_file_lines.append([p_id.lexeme, 'FFFFFFFF'])
			if t_w.type in ['INT', 'REAL', 'AINT', 'AREAL']:
				t_w.type = 'PP' + t_w.type
			else:
				t_w.type = 'ERR'
			node = scope_tree.search(green_node_stack)
			self.push_blue_node(node, Node('blue', p_id.lexeme, t_w.type), p_id.line_number)
			self.add_type(p_id, t_w.type)
			if p_id.lexeme in inherited:
				self.add_error(token.line_number, None, 2, 'Cannot have repeated parameters.')
			inherited.append(node.name)
			pl2_w = self.parameter_list2(inherited)
			parameter_list2_w.synthesized = pl2_w.synthesized
		elif token.lexeme == ')':
			parameter_list2_w.synthesized = inherited
		else:
			self.synch(['$', ';', ')'], [';'])
		return parameter_list2_w
		
	def compound_statement(self):
		global token
		compound_statement_w = Type_Wrapper(None, None, None, 0)
		if token.lexeme == 'begin':
			self.match(['begin'])
			self.compound_statement2()
		else:
			self.synch(['$', 'begin', '.', 'else', ';', 'end'], ['begin'])
		return compound_statement_w
		
	def compound_statement2(self):
		global token
		compound_statement2_w = Type_Wrapper(None, None, None, 0)
		if token.token_type == 1 or token.lexeme in ['begin', 'if', 'while', 'call']:
			self.statement_list()
			self.match(['end'])
		elif token.lexeme == 'end':
			self.match(['end'])
		else:
			self.synch(['$', 1, 'call', 'begin', 'if', 'while', 'end', '.', 'else', ';'], ['id', 'begin', 'if', 'while', 'call'])
		return compound_statement2_w
		
	def statement_list(self):
		global token
		statement_list_w = Type_Wrapper(None, None, None, 0)
		if token.token_type == 1 or token.lexeme in ['begin', 'if', 'while', 'call']:
			self.statement()
			self.statement_list2()
		else:
			self.synch(['$', 1, 'call', 'begin', 'if', 'while', 'end'], ['id', 'begin', 'if', 'while', 'call'])
		return statement_list_w
		
	def statement_list2(self):
		global token
		statement_list2_w = Type_Wrapper(None, None, None, 0)
		if token.lexeme == ';':
			self.match([';'])
			self.statement()
			self.statement_list2()
		elif token.lexeme != 'end':
			self.synch(['$', ';', 'end'], [';'])
		return statement_list2_w
		
	def statement(self):
		global token
		statement_w = Type_Wrapper(None, None, None, 0)
		if token.token_type == 1:
			v_w = self.variable()
			self.match([30])
			p_id = token
			e_w = self.expression()
			tmp1 = v_w.type
			tmp2 = e_w.type
			if tmp1[:2] == 'PP': tmp1 = tmp1[2:]
			if tmp2[:2] == 'PP': tmp2 = tmp2[2:]
			if tmp1 != tmp2 and tmp1 not in ['ERR', 'ERR*'] and tmp2 not in ['ERR', 'ERR*']:
				self.add_error(p_id.line_number, None, 2, 'Assignop operand types mismatched with each other.')
		elif token.lexeme == 'call':
			self.procedure_statement()
		elif token.lexeme == 'begin':
			self.compound_statement()
		elif token.lexeme == 'if':
			self.match(['if'])
			e_w = self.expression()
			if e_w.type != 'BOOL':
				self.add_error(token.line_number, None, 2, 'Conditional expression type is not boolean.')
			self.match(['then'])
			self.statement()
			self.statement2()
		elif token.lexeme == 'while':
			self.match(['while'])
			e_w = self.expression()
			if e_w.type != 'BOOL':
				self.add_error(token.line_number, None, 2, 'Conditional expression type is not boolean.')
			self.match(['do'])
			self.statement()
		else:
			self.synch(['$', 1, 'call', 'begin', 'if', 'while', 'else', ';', 'end'], ['id', 'call', 'begin', 'if', 'while'])
		return statement_w
		
	def statement2(self):
		global token
		statement2_w = Type_Wrapper(None, None, None, 0)
		if token.lexeme == 'else':
			self.match(['else'])
			self.statement()
		elif token.lexeme not in [';', 'end']:
			self.synch(['$', 'else', ';', 'end'], ['else'])
		return statement2_w
		
	def variable(self):
		global token
		variable_w = Type_Wrapper(None, None, None, 0)
		if token.token_type == 1:
			p_id = token
			self.match([1])
			v2_w = self.variable2(self.get_pointer(Node('blue', p_id.lexeme, None), p_id.line_number), p_id.lexeme)
			variable_w.type = v2_w.type
		else:
			self.synch(['$', 1, 30], ['id'])
		return variable_w
		
	def variable2(self, inherited, p_id):
		global token
		variable2_w = Type_Wrapper(None, None, None, 0)
		if token.lexeme == '[':
			self.match(['['])
			e_w = self.expression()
			self.match([']'])
			if e_w.type == 'INT' and inherited:
				if inherited.type in ['PPAINT', 'AINT']:
					variable2_w.type = 'INT'
				elif inherited.type in ['PPAREAL', 'AREAL']:
					variable2_w.type = 'REAL'
				elif inherited.type == 'ERR':
					variable2_w.type = 'ERR'
				else:
					variable2_w.type = 'ERR*'
					self.add_error(token.line_number, None, 2, 'Attempted to find index of non-array variable.')
			else:
				variable2_w.type = 'ERR*'
				self.add_error(token.line_number, None, 2, 'Attempted to use non-integer number or variable as array index.')
		elif token.token_type == 30:
			if inherited:
				if inherited.type in ['INT', 'REAL', 'PPINT', 'PPREAL', 'PROC']:
					variable2_w.type = inherited.type
				elif inherited.type == 'ERR':
					variable2_w.type = 'ERR'
				else:
					variable2_w.type = 'ERR*'
					self.add_error(token.line_number, None, 2, p_id + ' is not an assignable type.')
			else:
				variable2_w.type = 'ERR*'
				self.add_error(token.line_number, None, 2, p_id + ' is not an assignable type.')
		else:
			self.synch(['$', '[', 30], ['['])
		return variable2_w

	def procedure_statement(self):
		global token, green_node_stack, scope_tree
		procedure_statement_w = Type_Wrapper(None, None, None, 0)
		if token.lexeme == 'call':
			self.match(['call'])
			p_id = token
			self.match([1])
			self.procedure_statement2(self.get_pointer(Node('green', p_id.lexeme, 'PROC'), p_id.line_number))
		else:
			self.synch(['$', 'call', 'else', ';', 'end'], ['call'])
		return procedure_statement_w
		
	def procedure_statement2(self, inherited):
		global token
		procedure_statement2_w = Type_Wrapper(None, None, None, 0)
		if token.lexeme == '(':
			self.match(['('])
			self.expression_list(inherited)
			self.match(')')
		elif token.lexeme in [';', 'end', 'else']:
			if self.get_num_params(inherited) != 0:
				self.add_error(token.line_number, None, 2, 'Call to ' + inherited.name + ' requires ' + str(self.get_num_params(inherited)) + ' parameters.')
		else:
			self.synch(['$', '(', 'else', ';', 'end'], ['('])
		return procedure_statement2_w
		
	def expression_list(self, inherited):
		global token, scope_tree, green_node_stack
		expression_list_w = Type_Wrapper(None, None, None, 0)
		if token.token_type in [1, 32, 33, 34] or token.lexeme in ['not', '+', '-', '(']:
			e_w = self.expression()
			if inherited:
				if not inherited.blue_nodes or e_w.type != inherited.blue_nodes[0].type[2:]:
					self.add_error(token.line_number, None, 2, 'Type of parameter 1 for call to ' + inherited.name + ' does not match declared type.')
			el2_w = self.expression_list2(inherited, 2)
			expression_list_w.synthesized = el2_w.synthesized
		else:
			self.synch(['$', 1, 32, 33, 34, '(', 'not', '+', '-', ')'], ['id', 'num', 'not', '+', '-', '('])
		return expression_list_w
		
	def expression_list2(self, inherited, count):
		global token, scope_tree
		expression_list2_w = Type_Wrapper(None, None, None, 0)
		if token.lexeme == ',':
			self.match([','])
			e_w = self.expression()
			if inherited and self.get_num_params(inherited) > count - 1 and inherited.blue_nodes[count - 1].type[2:] != e_w.type:
				self.add_error(token.line_number, None, 2, 'Type of parameter ' + str(count) + ' for call to ' + inherited.name + ' does not match declared type.')
			count += 1
			el2_w = self.expression_list2(inherited, count)
			expression_list2_w.synthesized = el2_w.synthesized
		elif token.lexeme == ')':
			if inherited and self.get_num_params(inherited) > count - 1:
				self.add_error(token.line_number, None, 2, 'Procedure call to ' + inherited.name + ' has too few parameters.')
			elif inherited and self.get_num_params(inherited) < count - 1:
				self.add_error(token.line_number, None, 2, 'Procedure call to ' + inherited.name + ' has too many parameters.')
		else:
			self.synch(['$', ',', ')'], [','])
		return expression_list2_w

	def expression(self):
		global token
		expression_w = Type_Wrapper(None, None, None, 0)
		if token.token_type in [1, 32, 33, 34] or token.lexeme in ['not', '+', '-', '(']:
			p_id = token
			se_w = self.simple_expression()
			e2_w = self.expression2(se_w.type)
			expression_w.type = e2_w.type
		else:
			self.synch(['$', 1, 32, 33, 34, '(', 'not', '+', '-', ']', ')', ',', 'then', 'do', 'else', ';', 'end'], ['id', 'num', 'not', '+', '-', '('])
		return expression_w
		
	def expression2(self, inherited):
		global token
		expression2_w = Type_Wrapper(None, None, None, 0)
		if token.token_type == 2:
			self.match([2])
			se_w = self.simple_expression()
			if inherited == se_w.type:
				if inherited in ['INT', 'REAL']:
					expression2_w.type = 'BOOL'
				elif inherited == 'ERR*':
					expression2_w.type = 'ERR'
				else:
					expression2_w.type = 'ERR*'
					self.add_error(token.line_number, None, 2, 'Invalid operand types for relop.')
			else:
				expression2_w.type = 'ERR*'
				self.add_error(token.line_number, None, 2, 'Relop operand types mismatched with each other.')
		elif token.lexeme in ['end', 'then', 'else', 'do', ')', ']', ',', ';']:
			if inherited:
				expression2_w.type = inherited
			else:
				expression2_w.type = 'ERR*'
		else:
			self.synch(['$', 2, ']', ')', ',', 'then', 'do', 'else', ';', 'end'], ['relop'])
		return expression2_w
		
	def simple_expression(self):
		global token
		simple_expression_w = Type_Wrapper(None, None, None, 0)
		if token.token_type in [1, 32, 33, 34] or token.lexeme in ['not', '(']:
			t_w = self.term()
			se2_w = self.simple_expression2(t_w.type)
			simple_expression_w.type = se2_w.type
		elif token.lexeme in ['+', '-']:
			self.sign()
			t_w = self.term()
			if t_w.type in ['INT', 'REAL']:
				se2_w = self.simple_expression2(t_w.type)
			else:
				se2_w = self.simple_expression2('ERR*')
				self.add_error(token.line_number, None, 2, 'Sign is inappropriate for the given term type.')
			simple_expression_w.type = se2_w.type
		else:
			self.synch(['$', 1, 32, 33, 34, '(', 'not', '+', '-', 2, ']', ')', ',', 'then', 'do', 'else', ';', 'end'], ['id', 'num', 'not', '(', '+', '-'])
		return simple_expression_w
		
	def simple_expression2(self, inherited):
		global token
		simple_expression2_w = Type_Wrapper(None, None, None, 0)
		if token.token_type == 4:
			addop = token
			self.match([4])
			t_w = self.term()
			if inherited == t_w.type:
				if (addop.lexeme.lower() == 'or' and t_w.type != 'BOOL') or (addop.lexeme.lower() != 'or' and t_w.type not in ['INT', 'REAL']):
					se2_w = self.simple_expression2('ERR*')
					self.add_error(token.line_number, None, 2, 'Operand types mismatched with addop type.')
				elif t_w.type in ['BOOL', 'INT', 'REAL']:
					se2_w = self.simple_expression2(t_w.type)
			else:
				if inherited != 'ERR*' and t_w.type != 'ERR*':
					self.add_error(addop.line_number, None, 2, 'Addop operand types mismatched with each other.')
				se2_w = self.simple_expression2('ERR*')
			simple_expression2_w.type = se2_w.type
		elif token.token_type == 2 or token.lexeme in ['end', 'then', 'else', 'do', ')', ']', ',', ';']:
			simple_expression2_w.type = inherited
		else:
			self.synch(['$', 4, 2, ']', ')', ',', 'then', 'do', 'else', ';', 'end'], ['addop'])
		return simple_expression2_w
		
	def term(self):
		global token
		term_w = Type_Wrapper(None, None, None, 0)
		if token.token_type in [1, 32, 33, 34] or token.lexeme in ['not', '(']:
			f_w = self.factor()
			t2_w = self.term2(f_w.type)
			term_w.type = t2_w.type
		else:
			self.synch(['$', 1, 32, 33, 34, '(', 'not', 4, 2, ']', ')', ',', 'then', 'do', 'else', ';', 'end'], ['id', 'num', 'not', '('])
		return term_w
		
	def term2(self, inherited):
		global token
		term2_w = Type_Wrapper(None, None, None, 0)
		if token.token_type == 3:
			mulop = token.lexeme.lower()
			self.match([3])
			p_id = token
			f_w = self.factor()
			if inherited == f_w.type:
				if (mulop in ['*', 'div', '/'] and f_w.type != 'BOOL') or (mulop == 'mod' and f_w.type == 'INT') or (mulop == 'and' and f_w.type == 'BOOL'):
					t2_w = self.term2(f_w.type)
				else:
					if f_w.type != 'ERR*':
						self.add_error(token.line_number, None, 2, 'Operand types mismatched with mulop type.')
					t2_w = self.term2('ERR*')
			else:
				if inherited != 'ERR*':
					self.add_error(p_id.line_number, None, 2, 'Mulop operand types mismatched with each other.')
				t2_w = self.term2('ERR*')
			term2_w.type = t2_w.type
		elif token.token_type in [2, 4] or token.lexeme in ['end', 'then', 'else', 'do', ')', ']', ',', ';']:
			term2_w.type = inherited
		else:
			self.synch(['$', 3, 4, 2, ']', ')', ',', 'then', 'do', 'else', ';', 'end'], ['mulop'])
		return term2_w
		
	def factor(self):
		global token
		factor_w = Type_Wrapper(None, None, None, 0)
		if token.token_type == 1:
			p_id = token
			self.match([1])
			f2_w = self.factor2(self.get_pointer(Node('blue', p_id.lexeme, None), p_id.line_number), p_id)
			factor_w.type = f2_w.type
		elif token.token_type in [32, 33, 34]:
			num = token
			self.match([32, 33, 34])
			if num.token_type == 33:
				factor_w.type = 'INT'
			elif num.token_type in [32, 34]:
				factor_w.type = 'REAL'
		elif token.lexeme == '(':
			self.match(['('])
			e_w = self.expression()
			self.match([')'])
			factor_w.type = e_w.type
		elif token.lexeme == 'not':
			self.match(['not'])
			f_w = self.factor()
			if f_w.type in ['BOOL', 'ERR']:
				factor_w.type = f_w.type
			else:
				factor_w.type = 'ERR*'
				self.add_error(token.line_number, None, 2, '\'not\' used with non-boolean operand.')
		else:
			self.synch(['$', 1, 32, 33, 34, '(', 'not', 3, 4, 2, ']', ')', ',', 'then', 'do', 'else', ';', 'end'], ['id', 'num', '(', 'not'])
		return factor_w
		
	def factor2(self, inherited, p_id):
		global token
		factor2_w = Type_Wrapper(None, None, None, 0)
		if token.lexeme == '[':
			self.match(['['])
			e_w = self.expression()
			rbrack = token
			self.match([']'])
			if e_w.type == 'INT':
				if inherited:
					if inherited.type in ['PPAINT', 'AINT']:
						factor2_w.type = 'INT'
					elif inherited.type in ['PPAREAL', 'AREAL']:
						factor2_w.type = 'REAL'
					else:
						factor2_w.type = 'ERR*'
						self.add_error(rbrack.line_number, None, 2, 'Expression type is not an array.')
				else:
					factor2_w.type = 'ERR*'
					self.add_error(rbrack.line_number, None, 2, 'Expression type is not an array.')
			else:
				factor2_w.type = 'ERR*'
				self.add_error(rbrack.line_number, None, 2, 'Attempted to use non-integer number or variable as array index.')
		elif token.token_type in [2, 3, 4] or token.lexeme in ['end', 'then', 'else', 'do', ')', ']', ',', ';']:
			if inherited:
				if inherited.type in ['PPINT', 'PPREAL', 'PPAINT', 'PPAREAL']:
					factor2_w.type = inherited.type[2:]
				else:
					factor2_w.type = inherited.type
		else:
			self.synch(['$', '[', 3, 4, 2, ']', ')', ',', 'then', 'do', 'else', ';', 'end'], ['['])
		return factor2_w

	def sign(self):
		global token
		if token.lexeme == '+':
			self.match(['+'])
		elif token.lexeme == '-':
			self.match(['-'])
		else:
			self.synch(['$', '+', '-', 1, 32, 33, 34, '(', 'not'], ['+', '-'])