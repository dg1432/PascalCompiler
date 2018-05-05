# Project 1 - Lexical Analyzer
October 1, 2014

## Table of Contents
[**Introduction**](#introduction)

[**Methodology**](#methodology)

[**Implementation**](#implementation)

[**Discussion and Conclusions**](#discussion-and-conclusions)

[**References**](#references)

[**Appendix**](#appendix---sample-inputs-and-outputs)

## Introduction
The compilation process is made up of six main phases: lexical analysis, syntax analysis, semantic analysis, intermediate code generation, code optimization, and target code generation. The role of a lexical analyzer is to "read the input characters [from the source program] and produce as output a sequence of tokens that the parser uses for syntax analysis." (Aho 84) The largest part of this project is interpreting the stream of characters and classifying the resulting tokens as different types for use by the syntax analyzer, then next step of the compilation process.

## Methodology
The lexical analyzer is a fairly straightforward program that separates tokens from a source program file to a token file, where they are listed and assigned token numbers and attribute numbers.

The first step of lexical analysis is to go through the source program line by line and separate the tokens based on their type (ARITHOP, RELOP, ID, reserved word, etc.). This can be done by reading the line character by character and determining the type of machine the character should be sorted to in order to create a token of that type. If the character is invalid or does not meet the form that is specified by the lexical analyzer, it is reported in the output files as type LEXERR.

After the program is read in and the tokens are separated, the lexical analyzer then writes to a listing file each line of the source program, including any errors found for each line. It will also write the tokens it has kept track of to a token file. Finally, while scanning the source program, the lexical analyzer will keep track of identifiers that are not reserved words, and store them in a symbol table, without duplicates.

## Implementation
To implement the lexical analyzer, I decided to use the Python programming language. My program begins with creating all of the input and output files specific to the source programs, whether they have or do not have lexical errors in them, and passing them to the lexical analyzer. After being called by the driver, all the components necessary for the lexical analyzer to run are initialized. It then begins to loop through the passed source program line by line. In each loop, the line is written to the listing file as a string and to the buffer as a list of characters. Then, the program looks at the first character in the buffer and determines what type of character it is (i.e. letter, number, symbol, etc.) and places it in the string corresponding to the token type. From there, it loops through the rest of the characters in the buffer and sends them to their corresponding token type. When the last character in the buffer has been reached, the errors that have accumulated during the reading of the line are written to the listing file and the error list is cleared for the next line. Then, the tokens are written to the token file, including their type and attribute information. Finally, the buffer is emptied and the lexical analyzer loops to the next line of the source program. When the lexical analyzer reaches the end of the source program, it simply exits the loop and the program is complete.

When the characters are passed from the main loop, they go to a function full of if/elif/else statements to determine what type the character is. They are then passed to a function that decides which function the character goes to based on its type to be added to its respective token. My program has functionality for white space, relops, mulops, arithops, identifiers, numbers, and others.

The white space function, which catches spaces and blank lines, is simply passed over and the program continues.

The relop function, which catches colons, equal signs, and less than/greater than signs, adds the passed character to its respective string. If the character passed to it is a different type from the next character, the string is evaluated and stored as a token, and is then emptied.

The mulop and arithop functions, which catch multiplication and division signs and plus and minus signs, respectively, work similarly to the relop function.

The identifier function catches all valid identifiers of form (letter)(letter or number)... shorter than 10 characters. If this size is exceeded, an error is added to the error list and the token is typed LEXERR. Otherwise, the program loops through characters and adds them to the respective string until the next character is of a different type. It then will check if the identifier is a reserved word. If not, it is added to the symbol table if it hasn’t already. Finally, the identifier’s storage string is emptied.

The number function checks the character, which could be a number, a decimal point, or 'e.' In short, this function keeps a number variable to store the number that is passed to the function one character at a time. It checks if the integer is ten digits or less, the characteristic and mantissa of the number are each five characters or less, and the exponent two characters or less, and adds errors to the error list and changes the type to LEXERR otherwise. If the number is valid, it will be separated to either 'Integer,' 'Real,' or 'Long real.'

Finally, the other function takes care of any other symbols that are valid, including parentheses, brackets, semicolons, colons, commas, and dots not being used for numbers. Any other symbol passed to this function must be invalid since it did not fit with any other function.

## Discussion and Conclusions
When this project was first assigned, I immediately thought that this would be one of the hardest software projects I had taken on here at TU. However, I broke it up into smaller, more manageable pieces and found it easier to work on it. I split the project up into input/output functionality, character typing and determining the machine they need to be sorted to, and the machines themselves. The input/output coding did not take long, even though this was the first "real" program I had written in Python. Determining the types for the characters took a little more time, but after studying samples of Pascal code, I was able to determine how the different character types related to the different machine types. Writing the machines proved to be the toughest, but most important, part of this project. I worked out some examples on pencil and paper to more easily visualize how the characters should be added to strings, and in turn to token entries or errors.

Overall, the project ended up taking longer than I had hoped due to other classwork, but after splitting the project into bite-sized chunks, it ended up being slightly easier than I had originally expected. I look forward to proceeding with the next project, the syntax analyzer, and learning how exactly it contributes to the compilation process.

## References
Aho, Alfred V., Ravi Sethi, and Jeffrey D. Ullman. *Compilers: Principles, Techniques, and Tools*. 1st ed. Bell Laboratories, 1986. Print.

## Appendix - Sample Inputs and Outputs
### No errors (happy path)
#### Inputs
* [src\_program](SampleInputs/src_program_no_errors)
* [reserved\_words](SampleInputs/reserved_words)

#### Outputs
* [listing\_file](SampleOutputs/listing_file_without_errors)
* [token\_file](SampleOutputs/token_file_without_errors)
* [symbol\_file](SampleOutputs/symbols_without_errors)

### With errors (focus on lexical errors)
#### Inputs
* [src\_program](SampleInputs/src_program_with_errors)
* [reserved\_words](SampleInputs/reserved_words)

#### Outputs
* [listing\_file](SampleOutputs/listing_file_with_errors)
* [token\_file](SampleOutputs/token_file_with_errors)
* [symbol\_file](SampleOutputs/symbols_with_errors)

### With errors (focus on syntax errors)
#### Inputs
* [src\_program](SampleInputs/src_program_syntax_errors)
* [reserved\_words](SampleInputs/reserved_words)

#### Outputs
* [listing\_file](SampleOutputs/listing_file_syntax_errors)
* [token\_file](SampleOutputs/token_file_syntax_errors)
* [symbol\_file](SampleOutputs/symbols_syntax_errors)
