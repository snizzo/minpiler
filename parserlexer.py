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
'newline'
)

# Regular expression rules for simple tokens
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_EQUALS  = r'='
t_DIVIDE  = r'/'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'

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

def p_expression_binop(t):
    '''expression : expression PLUS expression
                | expression MINUS expression
                | expression TIMES expression
                | expression DIVIDE expression'''
    if t[2] == '+'  : t[0] = t[1] + t[3]
    elif t[2] == '-': t[0] = t[1] - t[3]
    elif t[2] == '*': t[0] = t[1] * t[3]
    elif t[2] == '/': t[0] = t[1] / t[3]

def p_expression_uminus(t):
    'expression : MINUS expression %prec UMINUS'
    t[0] = -t[2]

def p_expression_group(t):
    'expression : LPAREN expression RPAREN'
    t[0] = t[2]

def p_expression_number(t):
    'expression : NUMBER'
    t[0] = t[1]

def p_expression_name(t):
    'expression : NAME'
    t[0] = t[1]
    

def p_error(t):
    print("Syntax error at '%s'" % t.value)

parser = yacc.yacc()