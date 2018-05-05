# Projects 3/4 - Semantic Analysis and Memory Address Computations
January 15, 2015

## Table of Contents
[**Introduction**](#introduction)

[**Methodology**](#methodology)
* [**L-Attributed Definition**](#l---attributed-definition)

[**Implementation**](#implementation)

[**Discussion and Conclusions**](#discussion-and-conclusions)

[**References**](#references)

[**Appendix**](#appendix---sample-inputs-and-outputs)

## Introduction
The compilation process is comprised of six main phases: lexical analysis, syntax analysis, semantic analysis, intermediate code generation, code optimization, and target code generation.  The role of a semantic analyzer is to "[check] the source program for semantic errors and [gather] type information for the subsequent code-generation phase." (Aho 8)  In this project, the semantic analyzer performs type and scope checking, which are folded into the recursive descent parser constructed in Project 2.  Memory address computation acts as an extension to scope checking by simply computing the offset of each variable within each scope of the source program.

## Methodology
The type and scope checking were based on an L-Attributed Definition (LAD), which is illustrated below.  LADs heavily rely upon LL(1) grammars using recursive descent parsers, which were created as part of Project 2.  Inherited and synthesized attributes play an important role in type checking for LADs because they allow information to be passed between adjacent grammar productions.  Scope checking for LADs is performed by using a blue/green node list representing variables and new scope headers, respectively, as well as a green node pointer stack.  Finally, address computation is handled during type and scope checking by calculating the amount of memory required for each data type when a variable is declared in a new scope.

#### L-Attributed Definition
1.1 *program* &#8594; **program id** (1) **(** *identifier_list* **)** *;* (2) *program'* (3)
```
	(1) {offset := 0;
	 memory_list.append(id.lexeme, "FFFFFFFF");
	 node = create_green_node(id, "PGNAME");
	 push_green_node(node);
	 identifier_list.inherited := get_pointer(node)}
	(2) {program'.inherited := identifier_list.synthesized}
	(3) {popGreenStack()}
```

1.2.1 *program'* &#8594; *compound_statement* **.**
```
	{}
```

1.2.2 *program'* &#8594; (1) *subprogram_declarations compound_statement* **.**
```
	(1) {subprogram_declarations.inherited := program'.inherited}
```

1.2.3 *program'* &#8594; (1) *declarations* (2) *program"*
```
	(1) {declarations.inherited := program'.inherited}
	(2) {program".inherited := declarations.synthesized}
```

1.3.1 *program"* &#8594; *compound_statement* **.**
```
	{}
```

1.3.2 *program"* &#8594; (1) *subprogram_declarations compound_statement* **.**
```
	(1) {subprogram_declarations.inherited := program".inherited}
```

2.1 *identifier_list* &#8594; **id** (1) *identifier_list'* (2)
```
	(1) {memory_list.append(id.lexeme, "FFFFFFFF");
	 if (identifier_list.inherited <> NULL {
		  node = create_blue_node(id.lexeme, "PGPARM");
		  identifier_list'.inherited := get_pointer(node);}
	 else
		  identifier_list'.inherited := identifier_list.inherited}
	(2) {identifier_list.synthesized := identifier_list'.synthesized}
```

2.2.1 *identifier_list'* &#8594; **, id** (1) *identifier_list'<sub>1</sub>* (2)
```
	(1) {memory_list.append(id.lexeme, "FFFFFFFF");
	 if (identifier_list'.inherited <> NULL) {
		  node = create_blue_node(id.lexeme, "PGPARM");
		  identifier_list'_1.inherited := get_pointer(node)}
	 else
		  identifier_list'_1.inherited := identifier_list'.inherited}
	(2) {identifier_list'.synthesized := identifier_list'_1.synthesized}
```

2.2.2 *identifier_list'* &#8594; **&#949;**
```
	{identifier_list'.synthesized := identifier_list'.inherited}
```

3.1 *declarations* &#8594; **var id :** *type* **;** (1) *declarations'* (2)
```
	(1) {memory_list.append(id.lexeme, offset);
	 offset += type.size;
	 if (declarations.inherited <> NULL) {
		  node = create_blue_node(id.lexeme, type.type);
		  declarations'.inherited := get_pointer(node)}
	 else {
		  node = create_blue_node(id.lexeme, type.type);
		  declarations'.inherited := declarations.inherited}}
	(2) {declarations.synthesized := declarations'.synthesized}
```

3.2.1 *declarations'* &#8594; **var id :** *type* **;** (1) *declarations'<sub>1</sub>* (2)
```
	(1) {memory_list.append(id.lexeme, offset);
	 offset += type.size;
	 node = create_blue_node(id.lexeme, type.type);
	 declarations'_1.inherited := get_pointer(node)}
	(2) {declarations'.synthesized := declarations'_1.synthesized}
```

3.2.2 *declarations'* &#8594; **&#949;**
```
	{declarations'.synthesized := declarations'.inherited}
```

4.1.1 *type* &#8594; *standard_type* (1)
```
	(1) {type.type := standard_type.type
	 type.size := standard_type.size}
```

4.1.2 *type* &#8594; **array [ num .. num1 ] of** *standard_type* (1)
```
	(1){if (num.type <> INT || num1.type <> num.type) {
		  type.type := ERR*;
		  type.size := 0;
		  print("Array indices must both be numerical integers.")}
	 else if (num.val > num1.val) {
		  type.type := ERR*;
		  type.size := 0;
		  print("Invalid array range.")}
	 else {
		  if (standard_type.type = INT)
			   type.type := AINT;
		  else if (standard_type.type = REAL)
			   type.type := AREAL;
		  type.size := (num1.val – num.val + 1) * standard_type.size}}
```

5.1.1 *standard_type* &#8594; **integer** (1)
```
	(1) {standard_type.type := INT;
	 standard_type.size := 4}
```

5.1.2 *standard_type* &#8594; **real** (1)
```
	(1) {standard_type.type := REAL;
	 standard_type.size := 8}
```

6.1 *subprogram_declarations* &#8594; (1) *subprogram_declaration* **;** (2) *subprogram_declarations'* (3)
```
	(1) {subprogram_declaration.inherited := subprogram_declarations.inherited}
	(2) {subprogram_declarations'.inherited := subprogram_declaration.synthesized}
	(3) {subprogram_declarations.synthesized := subprogram_declarations'.synthesized}
```

6.2.1 *subprogram_declarations'* &#8594; (1) *subprogram_declaration* **;** (2) *subprogram_declarations'<sub>1</sub>* (3)
```
	(1) {subprogram_declaration.inherited := subprogram_declarations'.inherited}
	(2) {subprogram_declarations'_1.inherited := subprogram_declaration.synthesized}
	(3) {subprogram_declarations'.synthesized := subprogram_declarations'_1.synthesized}
```

6.2.2 *subprogram_declarations'* &#8594; **&#949;**
```
	{}
```

7.1 *subprogram_declaration* &#8594; (1) *subprogram_head* (2) *subprogram_declaration'* (3)
```
	(1) {subprogram_head.inherited := subprogram_declaration.inherited}
	(2) {subprogram_declaration'.inherited := subprogram_head.synthesized}
	(3) {subprogram_declaration.synthesized := subprogram_declaration'.synthesized}
```

7.2.1 *subprogram_declaration'* &#8594; (1) *declarations* (2) *subprogram_declaration"* (3)
```
	(1) {declarations.inherited := subprogram_declaration'.inherited}
	(2) {subprogram_declaration".inherited := declarations.synthesized}
	(3) {subprogram_declaration'.synthesized := subprogram_declaration".synthesized}
```

7.2.2 *subprogram_declaration'* &#8594; *compound_statement* (1)
```
	(1) {subprogram_declaration'.synthesized := subprogram_declaration'.inherited}
```

7.2.3 *subprogram_declaration'* &#8594; (1) *subprogram_declarations compound_statement* (2)
```
	(1) {subprogram_declarations.inherited := subprogram_declaration'.inherited}
	(2) {subprogram_declaration'.synthesized := subprogram_declarations.synthesized}
```

7.3.1 *subprogram_declaration"* &#8594; *compound_statement* (1)
```
	(1) {subprogram_declaration".synthesized := subprogram_declaration".inherited}
```

7.3.2 *subprogram_declaration"* &#8594; (1) *subprogram_declarations compound_statement* (2)
```
	(1) {subprogram_declarations.inherited := subprogram_declaration".inherited}
	(2) {subprogram_declaration".synthesized := subprogram_declarations.synthesized}
```

8.1 *subprogram_head* &#8594; **procedure id** (1) *subprogram_head'* (2)
```
	(1) {memory_list.append(id.lexeme, "FFFFFFFF");
	 offset := 0;
	 node = create_green_node(id.lexeme, "PROC");
	 if (subprogram_head.inherited <> NULL)
		  subprogram_head'.inherited := get_pointer(node)
	 else
		  subprogram_head'.inherited := NULL}
	(2) {subprogram_head.synthesized := subprogram_head.inherited}
```

8.2.1 *subprogram_head'* &#8594; (1) *arguments* **;** (2)
```
	(1) {arguments.inherited := subprogram_head'.inherited}
	(2) {subprogram_head'.synthesized := arguments.synthesized}
```

8.2.2 *subprogram_head'* &#8594; **;** (1)
```
	(1) {subprogram_head'.synthesized := subprogram_head'.inherited}
```

9.1 *arguments* &#8594; (1) **(** *parameter_list* **)** (2)
```
	(1) {parameter_list.inherited := arguments.inherited}
	(2) {arguments.synthesized := parameter_list.synthesized}
```

10.1 *parameter_list* &#8594; **id :** *type* (1) *parameter_list'* (2)
```
	(1) {memory_list.append(id.lexeme, "FFFFFFFF");
	 if (type.type = "INT")
		  node = create_blue_node(id.lexeme, "PPINT");
	 else if (type.type = "REAL")
		  node = create_blue_node(id.lexeme, "PPREAL");
	 else if (type.type = "AINT")
		  node = create_blue_node(id.lexeme, "PPAINT");
	 else if (type.type = "AREAL")
		  node = create_blue_node(id.lexeme, "PPAREAL");
	 else
		  node = create_blue_node(id.lexeme, "ERR");
	 parameter_list'.inherited := [node.name]}
	(2) {parameter_list.synthesized := parameter_list'.synthesized}
```

10.2.1 *parameter_list'* &#8594; **; id :** *type* (1) *parameter_list'<sub>1</sub>* (2)
```
	(1) {memory_list.append(id.lexeme, "FFFFFFFF");
	 if (type.type = "INT")
		  node = create_blue_node(id.lexeme, "PPINT");
	 else if (type.type = "REAL")
		  node = create_blue_node(id.lexeme, "PPREAL");
	 else if (type.type = "AINT")
		  node = create_blue_node(id.lexeme, "PPAINT");
	 else if (type.type = "AREAL")
		  node = create_blue_node(id.lexeme, "PPAREAL");
	 else
		  node = create_blue_node(id.lexeme, "ERR");
	 if (id.lexeme in parameter_list'.inherited)
		  print("Cannot have repeated parameters.");
	 inherited.append(node.name);
	 parameter_list'_1.inherited := parameter_list'.inherited}
	(2) {parameter_list'.synthesized := parameter_list'_1.synthesized}
```

10.2.2 *parameter_list'* &#8594; **&#949;** (1)
```
	(1) {parameter_list'.synthesized := parameter_list'.inherited}
```

11.1 *compound_statement* &#8594; **begin** *compound_statement'*
```
	{}
```

11.2.1 *compound_statement'* &#8594; *statement_list* **end**
```
	{}
```

11.2.2 *compound_statement'* &#8594; **end**
```
	{}
```

12.1 *statement_list* &#8594; *statement statement_list'*
```
	{}
```

12.2.1 *statement_list'* &#8594; **;** *statement statement_list'<sub>1</sub>*
```
	{}
```

12.2.2 *statement_list'* &#8594; **&#949;**
```
	{}
```

13.1.1 *statement* &#8594; *variable* **assignop** *expression* (1)
```
	(1) {if (variable.type <> expression.type && variable.type <> "ERR")
		  print("Assignop operand types mismatched with each other.")}
```

13.1.2 *statement* &#8594; *procedure_statement*
```
	{}
```

13.1.3 *statement* &#8594; *compound_statement*
```
	{}
```

13.1.4 *statement* &#8594; **if** *expression* (1) **then** *statement statement'*
```
	(1) {if (expression.type <> "BOOL")
		  print("Conditional expression type is not boolean.")}
```

13.1.5 *statement* &#8594; **while** *expression* (1) **do** *statement<sub>1</sub>*
```
	(1) {if (expression.type <> "BOOL")
		  print("Conditional expression type is not boolean.")}
```

13.2.1 *statement'* &#8594; **else** *statement*
```
	{}
```

13.2.2 *statement'* &#8594; **&#949;**
```
	{}
```

14.1 *variable* &#8594; **id** (1) *variable'* (2)
```
	(1) {variable'.inherited := get_pointer(id.lexeme)}
	(2) {variable.type := variable'.type}
```

14.2.1 *variable'* &#8594; **[** *expression* **]** (1)
```
	(1) {if (expression.type = "INT" && variable'.inherited <> NULL) {
		  if (variable'.inherited.type in ["PPAINT"|"AINT"])
			   variable'.type := "INT";
		  else if (variable'.inherited.type in ["PPAREAL"|"AREAL"])
			   variable'.type := "REAL";
		  else if (variable'.inherited.type = ERR)
			   variable'.type := "ERR";
		  else {
			   variable'.type := "ERR*";
			   print("Attempted to find index of non-array variable.")}}
	 else {
		  variable'.type := "ERR*";
		  print("Attempted to use invalid number or variable as array index.")}}
```

14.2.2 *variable'* &#8594; **&#949;** (1)
```
	(1) {if (variable'.inherited <> NULL)
		  if (variable'.inherited.type in ["INT"|"REAL"|"PPINT"|"PPREAL"|"PROC"])
			   variable'.type := variable'.inherited.type
		  else if (variable'.inherited.type = "ERR")
			   variable'.type := "ERR"
	 else
		  variable'.type := ERR*
		  print("Not an assignable type.")}
```

15.1 *procedure_statement* &#8594; **call id** (1) *procedure_statement'*
```
	(1) {procedure_statement'.inherited := getPointer(id)
```

15.2.1 *procedure_statement'* &#8594; (1) **(** *expression_list* **)**
```
	(1) {expression_list.inherited := procedure_statement'.inherited}
```

15.2.2 *procedure_statement'* &#8594; **&#949;**
```
	{}
```

16.1 *expression_list* &#8594; *expression* (1) *expression_list'* (2)
```
	(1) {if (expression_list.inherited <> NULL)
		  if (get_num_params(expression_list.inherited) == 0)
			   print("More than 0 parameters supplied for procedure call.");
		  if (expression_list.inherited.blue_nodes = NULL || expression.type <> expression_list.blue_nodes[0].type[2:])
			   print("Type of parameter 1 for procedure call does not match declared type.");
	 count := 2;
	 expression_list'.inherited := expression_list.inherited}
	(2) {expression_list.synthesized := expression_list'.synthesized}
```

16.2.1 *expression_list'* &#8594; **,** *expression* (1) *expression_list'<sub>1</sub>* (2)
```
	(1) {if (expression_list'.inherited <> NULL && get_num_params(expression_list'.inherited) > count – 1 && expression_list'.inherited.blue_nodes[count – 1].type[2:] <> expression.type)
		  print("Type of parameter " + count + " for procedure call does not match declared type.");
	 count += 1;
	 expression_list'_1.inherited := expression_list'.inherited}}
	(2) {expression_list'.synthesized := expression_list'_1.synthesized}
```

16.2.2 *expression_list'* &#8594; **&#949;** (1)
```
	(1) {if (expression_list'.inherited <> NULL && get_num_params(expression_list'.inherited) > count - 1)
		  print("Procedure call has too few parameters.")
	 else if (expression_list'.inherited <> NULL && get_num_params(expression_list'.inherited) < count - 1)
		  print("Procedure call has too many parameters.")}
```

17.1 *expression* &#8594; *simple_expression* (1) *expression'* (2)
```
	(1) {expression'.inherited := simple_expression.type}
	(2) {expression.type := expression'.type}
```

17.2.1 *expression'* &#8594; **relop** *simple_expression* (1)
```
	(1) {if (expression'.inherited = simple_expression.type) {
		  if (expression'.inherited in ["INT"|"REAL"])
			   expression'.type := "BOOL";
		  else if (expression'.inherited = "ERR*")
			   expression'.type := "ERR";
		  else {
			   expression'.type := "ERR*";
			   print("Invalid operand types for relop.")}}
	 else {
		  expression'.type := "ERR*";
		  print("Relop operand types mismatched with each other.")}}
```

17.2.2 *expression'* &#8594; **&#949;** (1)
```
	(1) {expression'.type := expression'.inherited}
```

18.1.1 *simple_expression* &#8594; *term* (1) *simple_expression'* (2)
```
	(1) {simple_expression'.inherited := term.type}
	(2) {simple_expression.type := simple_expression'.type}
```

18.1.2 *simple_expression* &#8594; *sign term* (1) *simple_expression'* (2)
```
	(1) {if (term.type in ["INT"|"REAL"])
		  simple_expression'.inherited := term.type;
	 else {
		  simple_expression'.inherited := "ERR*";
		  print("Sign is inappropriate for the given term type.")}}
	(2) {simple_expression.type := simple_expression'.type}
```

18.2.1 *simple_expression'* &#8594; **addop** *term* (1) *simple_expression'<sub>1</sub>* (2)
```
	(1) {if (simple_expression'.inherited = term.type) {
		  if ((addop.op = "OR" && term.type <> "BOOL") || (addop.op <> "OR" && term.type not in ["INT"|"REAL"])) {
			   simple_expression'1.inherited := "ERR*";
			   print("Operand types mismatched with addop type.")}
		  else if (term.type in ["BOOL"|"INT"|"REAL"])
			   simple_expression'1.inherited := term.type}
	 else {
		  if simple_expression'.inherited <> "ERR*"
			   print("Operand types mismatched with each other.");
		  simple_expression'_1.inherited := "ERR*"}}
	(2) {simple_expression'.type := simple_expression'_1.type}
```

18.2.2 *simple_expression'* &#8594; **&#949;** (1)
```
	(1) {simple_expression'.type := simple_expression'.inherited}
```

19.1 *term* &#8594; *factor* (1) *term'* (2)
```
	(1) {term'.inherited := factor.type}
	(2) {term.type := term'.type}
```

19.2.1 *term'* &#8594; **mulop** *factor* (1) *term'<sub>1</sub>* (2)
```
	(1) {if (term'.inherited = factor.type) {
		  if (((mulop.op in ["*"|"div"|"/"]) && factor.type <> "BOOL") || (mulop.op = "MOD" && factor.type = "INT") || (mulop.op = "AND" && factor.type = "BOOL"))
			   term'_1.inherited := factor.type
		  else
			   term'_1.inherited := "ERR*"
			   print("Operand types mismatched with mulop type.")}
	 else {
		  if term'.inherited <> "ERR*"
			   print("Operand types mismatched with each other.");
		  term'_1.inherited := "ERR*"}}
	(2) {term'.type := term'_1.type}
```

19.2.2 *term'* &#8594; **&#949;** (1)
```
	(1) {term'.type := term'.inherited}
```

20.1.1 *factor* &#8594; **id** (1) *factor'* (2)
```
	(1) {factor'.inherited := get_pointer(id)}
	(2) {factor.type := factor'.type}
```

20.1.2 *factor* &#8594; **num** (1)
```
	(1) {factor.type := num.type}
```

20.1.3 *factor* &#8594; **(** *expression* **)** (1)
```
	(1) {factor.type := expression.type}
```

20.1.4 *factor* &#8594; **not** *factor<sub>1</sub>* (1)
```
	(1) {if (factor1.type in ["BOOL"|"ERR"])
		  factor.type := factor_1.type
	 else {
		  factor.type = "ERR*";
		  print("'not' used with non-boolean operand.")}}
```

20.2.1 *factor'* &#8594; **[** *expression* **]** (1)
```
	(1) {if (expression.type = "INT") {
		  if (factor'.inherited <> NULL) {
			   if (factor'.inherited.type in ["PPAINT"|"AINT"])
				    factor'.type := "INT";
			   else if (factor'.inherited in ["PPAREAL"|"AREAL"])
				    factor'.type := "REAL";
			   else {
				    factor'.type := "ERR*";
				    print("Expression type is not an array.")}
		  else {
			   factor'.type := "ERR*";
			   print("Expression type is not an array.")}}
	 else {
		  print("Attempted to use invalid number or variable as array index.");
		  factor'.type := "ERR*"}}
```

20.2.2 *factor'* &#8594; **&#949;** (1)
```
	(1) {if (factor'.inherited <> NULL)
		  if (factor'.inherited.type = "PPINT")
			   factor'.type := "INT";
		  else if (factor'.inherited.type = "PPREAL")
			   factor'.type := "REAL";
		  else if (factor'.inherited.type = "PPAINT")
			   factor'.type := "AINT";
		  else if (factor'.inherited.type = "PPAREAL")
			   factor'.type := "AREAL";
		  else
			   factor'.type := factor'.inherited.type}
```

21.1.1 *sign* &#8594; **+**
```
	{}
```

21.1.2 *sign* &#8594; **–**
```
	{}
```

## Implementation
My implementation of the semantic analyzer and memory addresses is written using the Python programming language.  I began this project by modifying the lexical analyzer to pass the symbol file to the recursive descent parser so it could be modified there.  For type checking, I modified the nonterminal symbols in the recursive descent parser to have an inherited attribute, if necessary, and to return Type_Wrapper data structures, which have attributes type, synthesized, value, and size.  These were used to simulate the L-Attributed Definitions listed above.

For scope checking, I created a tree of Nodes and a stack of pointers to green Nodes.  Green Nodes represent scopes, such as program and procedure declarations, whereas blue Nodes represent associated parameters and variables declared within each of the scopes.  My Node data structures store color, name, type, children, and associated blue Nodes.  The Node tree searches for the current Node by using the green Node stack.  It begins at the bottom of the stack and matches that Node to the root of the Node tree, and works its way through the stack and tree until the node at the top of the stack is reached.

Finally, for memory address computation, I used a global variable called "offset" to keep track of the current offset for variables in each scope.  Integers take 4 bytes, reals take 8 bytes, and arrays take (array_size \* array_type) bytes.  "offset" is reset to 0 when a new scope is reached.  At the end, all of the data is recorded in an output file.


## Discussion and Conclusions
It took a couple of weeks for me to understand exactly what was expected of me in this project.  Once I finally understood how type and scope checking worked, this project became straightforward.  The type checking was the most difficult part of this project because I had to think through every possible type that any of the productions could take on and handle them accordingly.  Once I completed type checking, I just had to review my notes on scope checking and wrote the code for the blue/green nodes.  The memory address computation code was almost trivial because it made use of the code I had already written for the type and scope checking.  When I started this project, it seemed complicated and daunting, but after thinking through and reviewing what I needed to do, it became straightforward.

## References
Aho, Alfred V., Ravi Sethi, and Jeffrey D. Ullman. *Compilers: Principles, Techniques, and Tools*. 1st ed. Bell Laboratories, 1986. Print.

## Appendix - Sample Inputs and Outputs
### Test case 1
#### Inputs
* [src\_program](SampleInputs/src_program)

#### Outputs
* [listing\_file](SampleOutputs/listing_file)
* [symbol\_file](SampleOutputs/symbol_file)
* [mem\_addresses](SampleOutputs/mem_addresses)
