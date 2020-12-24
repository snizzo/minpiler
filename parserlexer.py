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
tokens = [
'LCURLY',
'RCURLY',
'NUMBER',
'PLUS',
'MINUS',
'TIMES',
'EQUALS',
'GREATER',
'LESS',
'DIVIDE',
'LPAREN',
'RPAREN',
'newline',
# 'QUOTE',
'STRING',
'PLUSEQUALS',
'MINUSEQUALS',
'TIMESEQUALS',
'DIVIDEEQUALS',
'COMMA',
'NAME'
] + list(reserved.values())

# Regular expression rules for simple tokens
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_EQUALS  = r'='
t_GREATER = r'>'
t_LESS    = r'<'
t_DIVIDE  = r'/'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
# t_QUOTE   = r'\"'
t_PLUSEQUALS = r'\+='
t_MINUSEQUALS = r'-='
t_TIMESEQUALS = r'\*='
t_DIVIDEEQUALS = r'/='
t_COMMA   = r','
t_LCURLY = r'\{'
t_RCURLY = r'\}'

# matching reserved words
def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.value = str(t.value)
    if str(t.value).lower() in reserved.keys():
        t.type = reserved[str(t.value).lower()]
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
    r'["][\w\s ()+-/*#@|\^&%=!><$\\\\]+["]'
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
    '''statements :   newline statements
                    | statement statements
                    | statement'''
    vmi.debug(t,"MAIN")

def p_statement_nl(t):
    '''statement : statement newline'''
    vmi.debug(t,"NL")

def p_statement_assign(t):
    '''statement : NAME EQUALS expression'''
    vmi.debug(t,"ASSIGN")
    vmi.stack.addVariable(t[1],t[3])
    vmi.encode("set {} {}".format(t[1],t[3]))
    # releasing temp var
    vmi.stack.releaseTempVar(t[3])

def p_statement_expr(t):
    'statement : expression'
    vmi.debug(t,"EXPR")
    #print(t[1])

def p_statement_while(t):
    '''statement : beforewhile WHILE expression LCURLY statements RCURLY'''
    vmi.debug(t,"REDUCEWHILE")
    jumpto = vmi.closeBlock()
    vmi.encode("jump {} {}".format(jumpto,t[3]))

def p_before_while(t):
    '''beforewhile :'''
    vmi.debug(t, "SHIFTWHILE")
    vmi.openBlock()

def p_statement_relop_greater_than(t):
    '''expression : expression GREATER expression'''
    vmi.debug(t,"GREATERTHAN")
    expr = "greaterThan {} {}".format(t[1],t[3])
    t[0] = expr

def p_statement_relop_less_than(t):
    '''expression : expression LESS expression'''
    vmi.debug(t,"LESSTHAN")
    expr = "lessThan {} {}".format(t[1],t[3])
    t[0] = expr

def p_statement_relop_greater_equal(t):
    '''expression : expression GREATER EQUALS expression'''
    vmi.debug(t,"GREATEREQUAL")
    expr = "greaterThanEq {} {}".format(t[1],t[4])
    t[0] = expr

def p_statement_relop_less_equal(t):
    '''expression : expression LESS EQUALS expression'''
    vmi.debug(t,"LESSEQUAL")
    expr = "lessThanEq {} {}".format(t[1],t[4])
    t[0] = expr

def p_binop_generic(t):
    '''expression : expression PLUS expression
                | expression MINUS expression
                | expression TIMES expression
                | expression DIVIDE expression'''
    vmi.debug(t,"BINOP_GENERIC")
    
    vname = vmi.stack.requestTempVar()
    if t[2] == '+'  : vmi.encode("op add {} {} {}".format(vname, t[1],t[3]))
    elif t[2] == '-': vmi.encode("op sub {} {} {}".format(vname, t[1],t[3]))
    elif t[2] == '*': vmi.encode("op mul {} {} {}".format(vname, t[1],t[3]))
    elif t[2] == '/': vmi.encode("op div {} {} {}".format(vname, t[1],t[3]))
    vmi.stack.releaseTempVar(t[1])
    vmi.stack.releaseTempVar(t[2])
    t[0] = vname

def p_statement_funcall(t):
    '''statement : NAME LPAREN expressions RPAREN'''
    vmi.debug(t,"FUNCALL")
    vmi.funcall(t[1],t[3])


def p_statement_binop_shortadd(t):
    '''statement :    NAME PLUSEQUALS expression'''
    vmi.debug(t,"BINOP_PLUSEQUALS")
    vmi.encode("op add {} {} {}".format(t[1],t[1],t[3]))


def p_statement_binop_shortsub(t):
    '''statement :    NAME MINUSEQUALS expression'''
    vmi.debug(t,"BINOP_MINUSEQUALS")
    vmi.encode("op sub {} {} {}".format(t[1],t[1],t[3]))


def p_statement_binop_shortmul(t):
    '''statement :    NAME TIMESEQUALS expression'''
    vmi.debug(t,"BINOP_TIMESEQUALS")
    vmi.encode("op mul {} {} {}".format(t[1],t[1],t[3]))


def p_statement_binop_shortdiv(t):
    '''statement :    NAME DIVIDEEQUALS expression'''
    vmi.debug(t,"BINOP_SHORTDIV")
    vmi.encode("op div {} {} {}".format(t[1],t[1],t[3]))

def p_expressions_list(t):
    '''expressions : expression COMMA expressions'''
    vmi.debug(t,"LIST")
    t[0] = t[1]+" "+t[3]

def p_expressions_void(t):
    '''expressions : expression'''
    vmi.debug(t,"VOID")
    t[0] = t[1]

def p_expression_uminus(t):
    'expression : MINUS expression %prec UMINUS'
    t[0] = -t[2]

def p_expression_group(t):
    'expression : LPAREN expression RPAREN'
    vmi.debug(t,"GROUP")
    t[0] = t[2]

def p_expression_number(t):
    'expression : NUMBER'
    vmi.debug(t,"NUMBER")
    t[0] = t[1]

def p_expression_string(t):
    'expression : STRING'
    vmi.debug(t,"STRING")
    t[0] = t[1]

def p_expression_name(t):
    'expression : NAME'
    vmi.debug(t,"NAME")
    t[0] = t[1]
    

def p_error(t):
    print("Syntax error at '%s'" % t.value)

parser = yacc.yacc()