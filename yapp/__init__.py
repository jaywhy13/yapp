import re
import inspect

from pyparsing import (
	Word, Literal, alphas, alphanums, nums, Optional,
	delimitedList, Group,
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
inop = Literal("in")
plusminus = plus | minus
multdivide = mult | divide | mod

# Groups
lbrace = Literal("(").suppress()
rbrace = Literal(")").suppress()

stack = []


def get_grammar(save_token_function=lambda: None):
	expr = Forward()
	atom = Forward()
	arg = expr
	args = delimitedList(arg)

	func_call = (ident + lbrace + Optional(args) + rbrace).setParseAction(save_token_function)

	atom << (func_call | (lbrace + expr.suppress() + rbrace) | ( decimal | integer | ident ).setParseAction(save_token_function) )

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
	"^" : lambda a,b: a ** b,
	"in" : lambda a,b: a in b
}

def reduce_stack(stack, environment={}):
	""" Reduces what's currently on the stack to a value
	"""
	op = stack.pop()
	if op in "+-*/^%":
		op2 = reduce_stack(stack)
		op1 = reduce_stack(stack)
		return op_map[op](op1, op2)
	elif re.search('^[a-zA-Z][a-zA-Z0-9_]*$', op):
		if op in environment:
			val = environment.get(op)
			if inspect.ismethod(val) or inspect.isfunction(val):
				argspec = inspect.getargspec(val)
				args = []
				num_args = len(argspec.args)
				for i in range(num_args):
					args.append(reduce_stack(stack))
				args.reverse()
				return val(*args)
			return val
	elif re.search('^[-+]?[0-9]+$', op):
		return long(op)
	else:
		return float(op)

def parse(expr, environment={}):
	stack = []
	def append_tokens(s, l, tokens):
		stack.append(tokens[0])
		#print("Adding token: %s" % tokens[0])

	grammar = get_grammar(append_tokens)
	result = grammar.parseString(expr)
	value = reduce_stack(stack, environment=environment)
	return value
