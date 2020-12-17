import ply.yacc as yacc
import ply.lex as lex

import vm

reserved = {
    'if' : 'IF',
    'then' : 'THEN',
    'else' : 'ELSE',
    'while' : 'WHILE'
}

# List of token names.   This is always required
tokens = (
'NUMBER',
'PLUS',
'MINUS',
'TIMES',
'EQUALS',
'DIVIDE',
'LPAREN',
'RPAREN',
'NAME',
'newline',
'QUOTE',
'STRING'
)

# Regular expression rules for simple tokens
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_EQUALS  = r'='
t_DIVIDE  = r'/'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_QUOTE   = r'\"'

# matching reserved words
def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.value = str(t.value)
    return t

# A regular expression rule with some action code
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    return t

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Regex that recognizes alphanumeric chars, 
# whitespace, and other special characters
def t_STRING(t):
    r'["][\w\s ()+-/*#@|\^&%=!><$]+["]'
    t.value = str(t.value)
    return t

lexer = lex.lex()

#
# ----------------- Parser -----------------
#

vmi = vm._vm

precedence = (
('left','PLUS','MINUS'),
('left','TIMES','DIVIDE'),
('right','UMINUS'),
)

# dictionary of names
names = { }


def p_statements(t):
    '''statements : statement newline statements
                    | statement newline
                    | statement'''

def p_statement_assign(t):
    '''statement : NAME EQUALS expression'''
    vmi.stack.addVariable(t[1],t[3])
    vmi.encode("set {} {}".format(t[1],t[3]))

def p_statement_expr(t):
    'statement : expression'
    print(t[1])

def p_statement_binop_add(t):
    '''statement :    NAME EQUALS expression PLUS expression'''
    vmi.encode("op add {} {} {}".format(t[1],t[3],t[5]))

def p_statement_binop_sub(t):
    '''statement :    NAME EQUALS expression MINUS expression'''
    vmi.encode("op sub {} {} {}".format(t[1],t[3],t[5]))

def p_statement_binop_mul(t):
    '''statement :    NAME EQUALS expression TIMES expression'''
    vmi.encode("op mul {} {} {}".format(t[1],t[3],t[5]))

def p_statement_binop_div(t):
    '''statement :    NAME EQUALS expression DIVIDE expression'''
    vmi.encode("op div {} {} {}".format(t[1],t[3],t[5]))

def p_expression_uminus(t):
    'expression : MINUS expression %prec UMINUS'
    t[0] = -t[2]

def p_expression_group(t):
    'expression : LPAREN expression RPAREN'
    t[0] = t[2]

def p_expression_number(t):
    'expression : NUMBER'
    t[0] = t[1]

def p_expression_string(t):
    'expression : STRING'
    t[0] = t[1]

def p_expression_quote(t):
    'expression : QUOTE STRING QUOTE'
    t[0] = t[1]+t[2]+t[3]

def p_expression_name(t):
    'expression : NAME'
    t[0] = t[1]
    

def p_error(t):
    print("Syntax error at '%s'" % t.value)

parser = yacc.yacc()