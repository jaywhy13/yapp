import re

from pyparsing import (
	Word, Literal, alphas, alphanums, nums, Optional,
	Combine,
	StringEnd,
	ZeroOrMore,
	Forward
)

# Terminal symbols =============================================================
# Variable names and including property access
ident = Word(alphas, alphanums + '_')

# Numbers
point = Literal(".")
number = Word(nums)
sign = Literal("+") | Literal("-")
integer = Combine(Optional(sign) + number)
decimal = Combine(integer + Optional(point + Optional(number)))

# Operators
plus = Literal("+")
minus = Literal("-")
mult = Literal("*")
divide = Literal("/")
exponent = Literal("^")
mod = Literal("%")
plusminus = plus | minus
multdivide = mult | divide | mod

# Groups
lbrace = Literal("(").suppress()
rbrace = Literal(")").suppress()

stack = []


def get_grammar(save_token_function=lambda: None):
	expr = Forward()
	atom = ( ( decimal | integer | ident ).setParseAction(save_token_function) | (lbrace + expr.suppress() + rbrace) )

	factor = Forward()
	factor << atom + ZeroOrMore( (exponent + factor).setParseAction(save_token_function) )

	term = factor + ZeroOrMore( (multdivide + factor).setParseAction(save_token_function) )

	expr << term + ZeroOrMore( (plusminus + term).setParseAction(save_token_function) )

	# Define the grammar now ...
	grammar = expr + StringEnd()
	return grammar

op_map = {
	"+" : lambda a,b: a + b,
	"-" : lambda a,b: a - b,
	"*" : lambda a,b: a * b,
	"/" : lambda a,b: a / b,
	"%" : lambda a,b: a % b,
	"^" : lambda a,b: a ** b
}

def reduce_stack(stack, environment={}):
	op = stack.pop()
	if op in "+-*/^%":
		op2 = reduce_stack(stack)
		op1 = reduce_stack(stack)
		return op_map[op](op1, op2)
	elif re.search('^[a-zA-Z][a-zA-Z0-9_]*$', op):
		if op in environment:
			return environment.get(op)
	elif re.search('^[-+]?[0-9]+$', op):
		return long(op)
	else:
		return float(op)

def parse(expr, environment={}):
	stack = []
	grammar = get_grammar(lambda s,l,tokens: stack.append(tokens[0]))
	result = grammar.parseString(expr)
	value = reduce_stack(stack, environment=environment)
	return value
