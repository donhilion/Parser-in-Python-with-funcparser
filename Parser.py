from funcparserlib.lexer import make_tokenizer, Token, LexerError
from funcparserlib.parser import (some, a, maybe, many, finished, skip,
	forward_decl, NoParseError)
from funcparserlib.parser import with_forward_decls

import pprint

class Char(object):
	def __init__(self, char):
		self.char = char

	def __str__(self):
		return "Char(" + str(self.char) + ")"

class Star(object):
	def __init__(self, exp):
		self.exp = exp

	def __str__(self):
		return "Star(" + str(self.exp) + ")"

class Or(object):
	def __init__(self, l, r):
		self.l = l
		self.r = r

	def __str__(self):
		return "Or(" + str(self.l) + "," + str(self.r) + ")"

class Lst(object):
	def __init__(self, lst):
		self.lst = lst

	def __str__(self):
		return "Lst(" + \
			reduce(lambda x,y: x + "," +y, (str(x) for x in self.lst)) + ")"

def tokenize(str):
	"""Returns tokens of the given string."""
	specs = [
		('Op',     (r'[|\(\)\*]',)),
		('Char',   (r'[A-Za-z0-9]',)),
	]
	useless = ['Space']
	t = make_tokenizer(specs)
	return [x for x in t(str) if x.type not in useless]

def parse(seq):
	"""Returns the AST of the given token sequence."""
	def eval_expr(z, list):
		return reduce(lambda s, (f, x): f(s, x), list, z)
	unarg = lambda f: lambda x: f(*x)
	const = lambda x: lambda _: x # like ^^^ in Scala

	tokval = lambda x: x.value # returns the value of a token
	op = lambda s: a(Token('Op', s)) >> tokval # return the value if token is Op
	op_ = lambda s: skip(op(s)) # checks if token is Op and ignores it
	toktype = lambda t: some(lambda x: x.type == t) >> tokval # checks type of token
	def lst(h,t):
		return [h,] + t

	makeop = lambda s, f: op(s) >> const(f)
	or_op = makeop('|', Or)
	
	char = with_forward_decls(lambda:
		toktype('Char') >> Char | op_('(') + exp + op_(')'))
	star = char + op_('*') >> Star | char

	lst2_exp = star + many(star) >> unarg(lst)
	lst_exp = lst2_exp >> Lst

	exp = lst_exp + many(or_op + lst_exp) >> unarg(eval_expr)

	return exp.parse(seq)

print(str(parse(tokenize("ab|(c|de)*fg*h"))))