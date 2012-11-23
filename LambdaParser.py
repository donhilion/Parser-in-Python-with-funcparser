# coding: utf-8

from funcparserlib.lexer import make_tokenizer, Token, LexerError
from funcparserlib.parser import (some, a, maybe, many, finished, skip,
	forward_decl, NoParseError)
from funcparserlib.parser import with_forward_decls

import pprint

depth = 0

class Variable(object):
	"""Variable node"""
	def __init__(self, name):
		self.name = str(name)
		self.__name__ = "Variable"

	def __str__(self):
		return "Variable(" + self.name + ")"

	def reduce(self):
		return self

class Abstraction(object):
	"""Abstraction node"""
	def __init__(self, v, body):
		self.v = str(v)
		self.body = body
		self.__name__ = "Abstraction"

	def __str__(self):
		return "Abstraction(" + self.v + " , " + str(self.body) + ")"

	def reduce(self):
		return self

class Application(object):
	"""Application node"""
	def __init__(self, fun, arg):
		self.fun = fun
		self.arg = arg
		self.__name__ = "Application"

	def __str__(self):
		return "Application(" + str(self.fun) + " , " + str(self.arg) + ")"

	def reduce(self):
		if self.fun.__name__ == "Abstraction":
			return substitute(self.fun.v, self.arg, self.fun.body)
		else:
			return Application(self.fun.reduce(), self.arg.reduce())
		

def tokenize(str):
	"""Returns tokens of the given string."""
	specs = [
		('Space',		(r'[ \t\r\n]+',)),
		('Dot',			(r'\.',)),
		('Name',		(r'[A-Za-z_][A-Za-z_0-9]*',)),
		('Lambda',		(u'λ',)),
		('Parentheses',	(r'[\(\)]',)),
	]
	useless = ['Space']
	t = make_tokenizer(specs)
	return [x for x in t(str) if x.type not in useless]

def parse(seq):
	"""Returns the AST of the given token sequence."""
	global depth
	unarg = lambda f: lambda x: f(*x)

	tokval = lambda x: x.value # returns the value of a token
	toktype = lambda t: some(lambda x: x.type == t) >> tokval # checks type of token
	paren = lambda s: a(Token('Parentheses', s)) >> tokval # return the value if token is Op
	paren_ = lambda s: skip(paren(s)) # checks if token is Op and ignores it

	def application(z, list):
		return reduce(lambda s, x: Application(s, x), list, z)

	depth = 0
	variable = lambda x: Variable(str(x)+":"+str(depth))
	def abstraction(x):
		global depth
		abst = Abstraction(str(x[0])+":"+str(depth), x[1])
		depth += 1
		return abst
	
	variable = toktype('Name') >> variable
	term = variable | with_forward_decls(lambda: paren_('(') + exp + paren_(')')) | \
		with_forward_decls(lambda: skip(toktype('Lambda')) + toktype('Name') + \
			skip(toktype('Dot')) + exp >> abstraction)

	exp = term + many(term) >> unarg(application)

	return exp.parse(seq)

def substitute(x, e2, e1):
	if e1.__name__ == "Variable":
		if e1.name != x:
			return e1
		else:
			return e2
	if e1.__name__ == "Abstraction":
		return Abstraction(e1.v, substitute(x, e2, e1.body))
	return Application(substitute(x, e2, e1.fun), substitute(x, e2, e1.arg))

def eval(ast):
	a = ast.reduce()
	return ast if a == ast else a.reduce()

ast = parse(tokenize(u"(λx.x)y"))
print(str(ast))
ast = eval(ast)
print(str(ast))

ast = parse(tokenize(u"(λx.x x) a"))
print(str(ast))
ast = eval(ast)
print(str(ast))

ast = parse(tokenize(u"(λx.(λx.x x) a) b"))
print(str(ast))
ast = eval(ast)
print(str(ast))