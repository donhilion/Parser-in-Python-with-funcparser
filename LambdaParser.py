# coding: utf-8

from funcparserlib.lexer import make_tokenizer, Token, LexerError
from funcparserlib.parser import (some, a, maybe, many, finished, skip,
	forward_decl, NoParseError)
from funcparserlib.parser import with_forward_decls

import pprint

class Variable(object):
	"""Variable node"""
	def __init__(self, name):
		self.name = str(name)

	def __str__(self):
		return "Variable(" + self.name + ")"

class Abstraction(object):
	"""Abstraction node"""
	def __init__(self, v, body):
		self.v = str(v)
		self.body = body

	def __str__(self):
		return "Abstraction(" + self.v + " , " + str(self.body) + ")"

class Application(object):
	"""Application node"""
	def __init__(self, fun, arg):
		self.fun = fun
		self.arg = arg

	def __str__(self):
		return "Application(" + str(self.fun) + " , " + str(self.arg) + ")"
		

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
	unarg = lambda f: lambda x: f(*x)

	tokval = lambda x: x.value # returns the value of a token
	toktype = lambda t: some(lambda x: x.type == t) >> tokval # checks type of token
	paren = lambda s: a(Token('Parentheses', s)) >> tokval # return the value if token is Op
	paren_ = lambda s: skip(paren(s)) # checks if token is Op and ignores it

	def application(z, list):
		return reduce(lambda s, x: Application(s, x), list, z)
	
	variable = toktype('Name') >> Variable
	term = variable | with_forward_decls(lambda: paren_('(') + exp + paren_(')')) | \
		with_forward_decls(lambda: skip(toktype('Lambda')) + toktype('Name') + \
			skip(toktype('Dot')) + exp >> unarg(Abstraction))

	exp = term + many(term) >> unarg(application)

	return exp.parse(seq)

print(str(parse(tokenize(u"(λx.x)x"))))
print(str(parse(tokenize(u"x y z"))))