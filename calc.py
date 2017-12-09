import math
import operator as op


PROMPT = " > "

# Data Types

SC_LIST = list
SC_SYMBOL = str
SC_NUMBER = (int, float)

class SC_ENV(dict):
    "An environment: a dict of {'var': val} pairs, with an outer Env."
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer
    def find(self, var):
        "Find the innermost Env where var appears."
        return self if (var in self) else self.outer.find(var)

class Procedure(object):
    "A user-defined Scheme procedure."
    def __init__(self, parms, body, env):
        self.parms, self.body, self.env = parms, body, env
    def __call__(self, *args): 
        return sc_eval(self.body, SC_ENV(self.parms, args, self.env))

def standard_env():
    e = SC_ENV()
    e.update(vars(math))
    e.update({
        "+": op.add,
        "-": op.sub,
        "*": op.mul,
        "/": op.truediv,
        "<": op.lt,
        ">": op.gt,
        ">=": op.ge,
        "<=": op.le,
        "=": op.eq,
        'abs': abs,
        'append': op.add,
        'apply': lambda proc, args: proc(*args),
        'begin': lambda *x: x[-1],
        'car': lambda x: x[0],
        'cdr': lambda x: x[1:],
        'cons': lambda x,y: [x] + y,
        'eq?': op.is_,
        'expt': pow,
        'equal?': op.eq,
        'length': len,
        'list': lambda *x: SC_LIST(x),
        'list?': lambda x: isinstance(x, SC_LIST),
        'map': map,
        'max': max,
        'min': min,
        'not': op.not_,
        'null?': lambda x: x == [],
        'number?': lambda x: isinstance(x, SC_NUMBER),
		'print': print,
        'procedure?': callable,
        'round': round,
        'symbol?': lambda x: isinstance(x, SC_SYMBOL),

    })
    return e

SC_DEFAULT_ENV = standard_env()

def sc_eval(x, env=SC_DEFAULT_ENV):
    "Eval"
    if isinstance(x, SC_SYMBOL):
        return env.find(x)[x]
    elif not isinstance(x, SC_LIST):
        return x
    
    op, *args = x
    if op == 'quote':
        return args[0]
    elif op == 'if':
        (cond, if_part, else_part) = args
        exp = (if_part if sc_eval(cond, env) else else_part)
        return sc_eval(exp, env)
    elif op == 'define':
        (symbol, exp) = args
        env[symbol] = sc_eval(exp, env)
    elif op == 'set!':
        (symbol, exp) = args
        env.find(symbol)[symbol] = sc_eval(exp, env)
    elif op == 'lambda':
        (parms, body) = args
        return Procedure(parms, body, env)
    else:                        # procedure call
        proc = sc_eval(op, env)
        vals = [sc_eval(arg, env) for arg in args]
        return proc(*vals)


def sc_parse_tokens(tokens):

    if len(tokens) == 0:
        raise SyntaxError('No tokens found.')

    token = tokens.pop(0)

    if token == '(':
        L = []

        while tokens[0] != ')':
            L.append(sc_parse_tokens(tokens))

        tokens.pop(0)

        return L
    elif token == ')':
        raise SyntaxError('Unexpected token.')
    else:
        return sc_type(token)


def sc_type(token):
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return SC_SYMBOL(token)

def sc_tokenize(string):
    return string.replace('(', ' ( ').replace(')', ' ) ').split()

def sc_parse(string):
    return sc_parse_tokens(sc_tokenize(string))

def repl(prompt=PROMPT):
    "Read eval, and print loop."
    while(True):
        val = sc_eval(sc_parse(input(prompt)))
        if val is not None: 
            print(sch_str(val))

def sch_str(exp):
    "Convert a Python object back into a Scheme-readable string."
    if isinstance(exp, SC_LIST):
        return '(' + ' '.join(map(sch_str, exp)) + ')'
    else:
        return str(exp)

if __name__ == '__main__':
    repl()
