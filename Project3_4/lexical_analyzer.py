'''
@author David Glover
CS 4013 - Compiler Construction
Project 3 and 4 - Type and Scope Checking and
				  Memory Address Computations
January 15, 2015
'''

from token import *
from recursive_descent import *
import random
import sys
import os

# Initialize static variables
MAX_BUFFER_SIZE = 72
ID_LENGTH = INT_LENGTH = 10
X_LENGTH = Y_LENGTH = 5
Z_LENGTH = 2

class Lexical_Analyzer:
    def __init__(self, source_file, listing_file, token_file, symbol_file, memory_file):
        # Variables shared with other functions
        global error_list, token_list, function_list, reserved_words_list, symbol_list
        global token, relop, mulop, addop, number, other, is_real, has_exponent
        global int_part, real_part, exponent, number_is_valid, line_number, token_list_rd
        global hex_list

        # Initialize variables
        int_part = real_part = exponent = ''
        line_number = 1
        lex_buffer = []
        error_list = []
        reserved_words_list = []
        token_list = []
        symbol_list = []
        token_list_rd = []
        hex_list = []
        listing_file_list = []
        token = relop = mulop = addop = number = other = ''
        number_is_valid = True
        is_real = has_exponent = False

        # Read in data from the reserved words file
        reserved_words_file = open(os.path.abspath('../Data/reserved_words'), 'r')
        for line in reserved_words_file:
            words = line.split(' ')
            reserved_words_list.append(Token(line_number, words[0], int(words[1]), words[2], int(words[3]), words[4]))

        # Write the token file header
        token_file.write('Line No.\tLexeme\t\t\t\tToken Type\t\t\t\tAttribute/Address\n')
        
        for line in source_file:
            line = line.strip()
            listing_file_list.append(str(line_number) + '\t\t' + line + '\n')

            if len(line) > MAX_BUFFER_SIZE:
                error_list.append('LEXERR: Line exceeds buffer size')

            # Fill the buffer
            for char in line:
                lex_buffer.append(char)

            # Evaluate the first char of the buffer if it is not empty
            next_char_type = curr_char_type = -1
            if lex_buffer:
                curr_char_type = self.pick_machine(lex_buffer[0])
            else:
                curr_char_type = 0
            if len(lex_buffer) >= 2 and curr_char_type == self.pick_machine(lex_buffer[1], curr_char_type):
                self.pick_function(curr_char_type, lex_buffer[0], False, symbol_file)

            # Evaluate the rest of the buffer
            for i in range(len(lex_buffer)):
                next_char_type = self.pick_machine(lex_buffer[i], curr_char_type)
                if next_char_type != curr_char_type or i > 1:
                    self.pick_function(curr_char_type, lex_buffer[i - 1], next_char_type != curr_char_type, symbol_file)
                curr_char_type = next_char_type
            if lex_buffer:
                self.pick_function(curr_char_type, lex_buffer[len(lex_buffer) - 1], True, symbol_file)

            # Write all the errors for the line to the listing file, if any
            while len(error_list) >= 1:
                listing_file_list.append(error_list.pop(0) + '\n')

            # Pretty print the tokens for the line to the token file, if any
            while len(token_list) >= 1:
                tkn = token_list.pop(0)
                token_list_rd.append(TokenRD(tkn.line_number, tkn.lexeme, tkn.token_type, tkn.attribute))
                tabs = '\t\t\t\t\t'
                token_file.write(str(line_number) + '\t\t\t' + str(tkn.lexeme) +
                tabs[0:len(tabs) - len(str(tkn.lexeme)) / 4] + str(tkn.token_type) +
                '\t(' + str(tkn.token) + ')' + tabs[0:len(tabs) - ((len(str(tkn.token)) + 2) / 4)] +
                str(tkn.attribute_type) + tabs[0:len(tabs) - len(str(tkn.attribute_type)) / 4 - 2] +
                '(' + tkn.attribute + ')' + '\n')

            # Empty the buffer for the next line
            while len(lex_buffer) >= 1:
                lex_buffer.pop()

            line_number += 1

        # Write EOF to the token file
        token_file.write(str(line_number - 1) + '\t\t\t$\t\t\t\t\t7\t(EOF)\t\t\t\t0\t\t\t(NULL)')

        # Close all files
        reserved_words_file.close()
        source_file.close()
        token_file.close()

        # Begin parsing the tokens
        token_list_rd.append(TokenRD(line_number - 1, '$', 7, 0))
        Recursive_Descent(token_list_rd, listing_file_list, listing_file, symbol_list, symbol_file, memory_file)

    def pick_machine(self, char, char_type = None):
        if not char or char == ' ':
            return 0
        elif char in ['=', ':', '<', '>']:
            return 1
        elif char in ['*', '/']:
            return 2
        elif char in ['+', '-']:
            return 3
        if not char_type:
            try:
                if char.isalpha():
                    return 4
                elif 9 >= int(char) >= 0:
                    return 5
            except:
                return 6
        else:
            try:
                if char_type == 4 and 9 >= int(char) >= 0:
                    return 4
                elif 9 >= int(char) >= 0:
                    return 5
            except:
                if char_type == 5 and char.lower() in ['.', 'e']:
                    return 5
                elif char.isalpha():
                    return 4
                else:
                    return 6

    def pick_function(self, char_type, char, is_last_char, sym_file):
        if char_type == 1:
            self.relop(char, is_last_char)
        elif char_type == 2:
            self.mulop(char, is_last_char)
        elif char_type == 3:
            self.addop(char, is_last_char)
        elif char_type == 4:
            self.identifier(char, is_last_char, sym_file)
        elif char_type == 5:
            self.number(char, is_last_char, sym_file)
        elif char_type == 6:
            self.other(char, is_last_char)

    def relop(self, char, is_last_char):
        global relop, line_number
        relop += char
        if is_last_char:
            if relop == ':=':
                token_list.append(Token(line_number, relop, 30, 'ASSIGNOP', 0, 'NULL'))
            elif relop == '>':
                token_list.append(Token(line_number, relop, 2, 'RELOP', 0, 'GT'))
            elif relop == '<':
                token_list.append(Token(line_number, relop, 2, 'RELOP', 2, 'LT'))
            elif relop == '>=':
                token_list.append(Token(line_number, relop, 2, 'RELOP', 3, 'GE'))
            elif relop == '<=':
                token_list.append(Token(line_number, relop, 2, 'RELOP', 4, 'LE'))
            elif relop == '<>':
                token_list.append(Token(line_number, relop, 2, 'RELOP', 5, 'NE'))
            elif relop == '=':
                token_list.append(Token(line_number, relop, 2, 'RELOP', 6, 'EQ'))
            elif relop == ':':
                token_list.append(Token(line_number, relop, 2, 'RELOP', 7, 'COLON'))
            relop = ''

    def mulop (self, char, is_last_char):
        global mulop, line_number
        mulop += char
        if is_last_char:
            if mulop == '*':
                token_list.append(Token(line_number, mulop, 3, 'MULOP', 1, 'MULT'))
            else:
                token_list.append(Token(line_number, mulop, 3, 'MULOP', 2, 'DIV'))
            mulop = ''

    def addop(self, char, is_last_char):
        global addop, line_number
        addop += char
        if is_last_char:
            if addop == '+':
                token_list.append(Token(line_number, addop, 4, 'ADDOP', 1, 'ADD'))
            else:
                token_list.append(Token(line_number, addop, 4, 'ADDOP', 2, 'SUB'))
            addop = ''

    def identifier(self, char, is_last_char, sym_file):
        global token, line_number
        token += char
        if is_last_char:
            if len(token) > ID_LENGTH:
                error_list.append('LEXERR: Token exceeded max length: ' + token)
                token_list.append(Token(line_number, token, 99, 'LEXERR', 1, 'EXTRA LONG TKN'))
                other = ''
                token = ''
                return

            # Check if the token is a reserved word
            for word in reserved_words_list:
                if word.lexeme == token:
                    token_list.append(Token(line_number, word.lexeme, word.token_type, word.token, word.attribute_type, word.attribute.strip('\n')))
                    token = ''
                    return
            self.add_id(token)
            self.check_symbols(sym_file)

    def number(self, char, is_last_char, sym_file):
        global number, is_real, has_exponent, int_part, real_part, exponent, number_is_valid, line_number
        number += char
        if char == '.':
            if number[len(number) - 2: len(number)] == '..':
                token_list.append(Token(line_number, number.rstrip('..'), 33, 'INTEGER', 0, 'NULL'))
                token_list.append(Token(line_number, '..', 27, 'DOT DOT', 0, 'NULL'))
                has_exponent = is_real = False
                number_is_valid = True
                number = int_part = real_part = exponent = ''
                return
            is_real = True
            if not is_last_char:
                return

        elif char.lower() == 'e':
            has_exponent = True
            if not is_last_char:
                return
            char = ''

        if has_exponent:
            exponent += char
        elif is_real:
            real_part += char
        else:
            int_part += char

        if is_last_char:
            if len(int_part) > X_LENGTH and is_real:
                error_list.append('LEXERR: Extra long characteristic: ' + number)
                token_list.append(Token(line_number, number, 99, 'LEXERR', 2, 'EXTRA LONG CHAR'))
                number_is_valid = False
            if len(real_part) > Y_LENGTH and is_real:
                error_list.append('LEXERR: Extra long mantissa: ' + number)
                token_list.append(Token(line_number, number, 99, 'LEXERR', 3, 'EXTRA LONG MANT'))
                number_is_valid = False
            if len(exponent) > Z_LENGTH and has_exponent:
                error_list.append('LEXERR: Extra long exponent: ' + number)
                token_list.append(Token(line_number, number, 99, 'LEXERR', 4, 'EXTRA LONG EXP'))
                number_is_valid = False
            if len(int_part) > INT_LENGTH and not is_real:
                error_list.append('LEXERR: Extra long integer: ' + int_part)
                token_list.append(Token(line_number, int_part, 99, 'LEXERR', 5, 'EXTRA LONG INT'))
                number_is_valid = False

            if number_is_valid:
                if has_exponent:
                    # |longreal|
                    if exponent and is_real and real_part and int_part:
                        token_list.append(Token(line_number, number, 32, 'LONG REAL', 0, 'NULL'))
                    # |dot|int|id|
                    elif is_real and real_part and not int_part:
                        token_list.append(Token(line_number, '.', 28, 'DOT', 0, 'NULL'))
                        token_list.append(Token(line_number, real_part, 33, 'INTEGER', 0, 'NULL'))
                        self.add_id('E' + exponent)
                        self.check_symbols(sym_file, 'E' + exponent)
                    # |int|dot|id|
                    elif is_real and not real_part and int_part:
                        token_list.append(Token(line_number, int_part, 33, 'INTEGER', 0, 'NULL'))
                        token_list.append(Token(line_number, '.', 28, 'DOT', 0, 'NULL'))
                        self.add_id('E' + exponent)
                        self.check_symbols(sym_file, 'E' + exponent)
                    # |dot|id|
                    elif is_real and not real_part and not int_part:
                        token_list.append(Token(line_number, '.', 28, 'DOT', 0, 'NULL'))
                        self.add_id('E' + exponent)
                        self.check_symbols(sym_file, 'E' + exponent)
                    # |int|id|
                    elif not is_real and not real_part and int_part:
                        token_list.append(Token(line_number, int_part, 33, 'INTEGER', 0, 'NULL'))
                        self.add_id('E' + exponent)
                        self.check_symbols(sym_file, 'E' + exponent)
                    # |id|
                    elif not is_real and not real_part and not int_part:
                        self.add_id('E' + exponent)
                        self.check_symbols(sym_file, 'E' + exponent)
                    # |real|id|
                    elif not exponent and is_real and real_part and int_part:
                        token_list.append(Token(line_number, int_part + '.' + real_part, 34, 'REAL', 0, 'NULL'))
                        self.add_id('E')
                        self.check_symbols(sym_file, 'E')
                elif is_real and not has_exponent:
                    if real_part:
                        if int_part:
                            # |real|
                            token_list.append(Token(line_number, number, 34, 'REAL', 0, 'NULL'))
                        else:
                            # |dot|int|
                            token_list.append(Token(line_number, '.', 28, 'DOT', 0, 'NULL'))
                            token_list.append(Token(line_number, real_part, 33, 'INTEGER', 0, 'NULL'))
                    else:
                        if int_part:
                            # |int|dot|
                            token_list.append(Token(line_number, int_part, 33, 'INTEGER', 0, 'NULL'))
                            token_list.append(Token(line_number, '.', 28, 'DOT', 0, 'NULL'))
                elif not is_real and not has_exponent and int_part:
                    # |int|
                    token_list.append(Token(line_number, number, 33, 'INTEGER', 0, 'NULL'))
            has_exponent = is_real = False
            number_is_valid = True
            number = int_part = real_part = exponent = ''

    def other(self, char, is_last_char):
        global other, line_number
        other += char
        if is_last_char or char != '.':
            if other == ';':
                token_list.append(Token(line_number, other, 23, 'SEMICOLON', 0, 'NULL'))
            elif other == '(':
                token_list.append(Token(line_number, other, 24, 'LEFT PAREN', 0, 'NULL'))
            elif other == ')':
                token_list.append(Token(line_number, other, 25, 'RIGHT PAREN', 0, 'NULL'))
            elif other == ',':
                token_list.append(Token(line_number, other, 26, 'COMMA', 0, 'NULL'))
            elif char == '.':
                if other == '..':
                    token_list.append(Token(line_number, other, 27, 'DOT DOT', 0, 'NULL'))
                else:
                    token_list.append(Token(line_number, other, 28, 'DOT', 0, 'NULL'))
            elif other == '[':
                token_list.append(Token(line_number, other, 29, 'OPEN BRACKET', 0, 'NULL'))
            elif other == ']':
                token_list.append(Token(line_number, other, 30, 'CLOSE BRACKET', 0, 'NULL'))
            elif other == ':':
                token_list.append(Token(line_number, other, 31, 'COLON', 0, 'NULL'))
            else:
                error_list.append('LEXERR: Unrecognized symbol: ' + other)
                token_list.append(Token(line_number, other, 99, 'LEXERR', 6, 'UNREC SYM'))
            other = ''

    def add_id(self, lex):
        global symbol_list, token_list, line_number
        hex_rand = '%00000008x' % random.randrange(16 ** 8)
        while hex_rand in hex_list:
            hex_rand = '%00000008x' % random.randrange(16 ** 8)
        hex_list.append(hex_rand)
        for word in symbol_list:
            if lex == word[0]:
                hex_rand = word[1]
                break
        token_list.append(Token(line_number, lex, 1, 'ID', hex_rand, 'PTR TO SYM TAB'))

    def check_symbols(self, sym_file, tok = None):
        # Check if the token is in the symbol list.  Add if it is not.
        global symbol_list, token, token_list
        if not tok:
            for word in symbol_list:
                if token == word[0]:
                    token = ''
                    return
            symbol_list.append([token, token_list[len(token_list) - 1].attribute_type, None])
            token = ''
        else:
            for word in symbol_list:
                if tok == word[0]:
                    return
            symbol_list.append([tok, token_list[len(token_list) - 1].attribute_type, None])