from funcparserlib.lexer import make_tokenizer, Token, LexerError
from funcparserlib.parser import (some, a, maybe, many, finished, skip,
	forward_decl, NoParseError)
from funcparserlib.parser import with_forward_decls

from re import VERBOSE
import pprint

class Const(object):
	"""Const node"""
	def __init__(self, integer):
		self.value = int(integer)

	def __str__(self):
		return "Const(" + str(self.value) + ")"

class Plus(object):
	"""Plus node"""
	def __init__(self, l, r):
		self.l = l
		self.r = r

	def __str__(self):
		return "Plus(" + str(self.l) + " , " + str(self.r) + ")"

class Minus(object):
	"""Minus node"""
	def __init__(self, l, r):
		self.l = l
		self.r = r

	def __str__(self):
		return "Minus(" + str(self.l) + " , " + str(self.r) + ")"

class Times(object):
	"""Times node"""
	def __init__(self, l, r):
		self.l = l
		self.r = r

	def __str__(self):
		return "Times(" + str(self.l) + " , " + str(self.r) + ")"

class Div(object):
	"""Div node"""
	def __init__(self, l, r):
		self.l = l
		self.r = r

	def __str__(self):
		return "Div(" + str(self.l) + " , " + str(self.r) + ")"

class Call(object):
	"""Call node"""
	def __init__(self, fun, args):
		self.fun = fun
		self.args = args

	def __str__(self):
		return "Call(" + str(self.fun) + " , {" + (reduce(lambda x, y: x+y, \
			((str(x) + ", ") for x in self.args)))[:-2] + "})"
		

def tokenize(str):
	"""Returns tokens of the given string."""
	specs = [
		('Space',  (r'[ \t\r\n]+',)),
#		('String', (ur'"(%(unescaped)s | %(escaped)s)*"' % regexps, VERBOSE)),
		('Number', (r'''
			(0|([1-9][0-9]*))   # Int
			''', VERBOSE)),
		('Op',     (r'[\-+/*\(\),]',)),
		('Name',   (r'[A-Za-z_][A-Za-z_0-9]*',)),
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
	#lst = lambda head, tail: (head,) + tail
	def lst(h,t):
		return [h,] + t
	call = lambda x: Call(x[0], x[1])

	makeop = lambda s, f: op(s) >> const(f)

	add = makeop('+', Plus)
	sub = makeop('-', Minus)
	mul = makeop('*', Times)
	div = makeop('/', Div)

	def make_const(i):
		return const(int(i))

	number = toktype('Number') >> Const

	mul_op = mul | div
	add_op = add | sub

	factor = with_forward_decls(lambda:
		number | op_('(') + exp + op_(')'))
	term = factor + many(mul_op + factor) >> unarg(eval_expr)
	math = term + many(add_op + term) >> unarg(eval_expr)
	exp_lst = with_forward_decls(lambda:
		exp + many(op_(',') + exp) >> unarg(lst))
	call = toktype('Name') + op_('(') + exp_lst + op_(')') >> call
	exp = math | call

	return exp.parse(seq)

print(str(parse(tokenize("42-5*(3+12)"))))
print(str(parse(tokenize("g(42-21,f(5))"))))