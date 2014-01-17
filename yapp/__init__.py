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
import pyparsing

from yapp.exceptions import *

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
gte = Literal(">=")
lte = Literal("<=")
gt = Literal(">")
lt = Literal("<")
relational = gte | lte | gt | lt

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

	rel_term = term + ZeroOrMore( (relational + term).setParseAction(save_token_function) )

	expr << rel_term + ZeroOrMore( (plusminus + rel_term).setParseAction(save_token_function) )

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
	"in" : lambda a,b: a in b,
	">" : lambda a,b : a > b,
	"<" : lambda a,b : a < b,
	">=" : lambda a,b : a >= b,
	"<=" : lambda a,b : a <= b,
}

function_map = {
	"not" : lambda x: not x
}

VARIABLE_REGEX = '^[a-zA-Z][a-zA-Z0-9_]*$'

def reduce_stack(stack, environment={}, fail_silently=True):
	""" Reduces what's currently on the stack to a value
	"""
	op = stack.pop()
	if op in op_map.keys():
		op2 = reduce_stack(stack, environment, fail_silently)
		op1 = reduce_stack(stack, environment, fail_silently)
		return op_map[op](op1, op2)
	elif re.search(VARIABLE_REGEX, op):
		if op in environment:
			val = environment.get(op)
			if inspect.ismethod(val) or inspect.isfunction(val):
				argspec = inspect.getargspec(val)
				args = []
				num_args = len(argspec.args)
				for i in range(num_args):
					args.append(reduce_stack(stack, environment, fail_silently))
				args.reverse()
				return val(*args)
			return val
		else:
			if not fail_silently:
				raise VariableMissingException("%s is not in the environment" % op, op)
	elif re.search('^[-+]?[0-9]+$', op):
		return long(op)
	else:
		return float(op)

def parse(expr, environment={}, fail_silently=True):
	full_environment = function_map.copy()
	full_environment.update(environment)
	stack = []
	def append_tokens(s, l, tokens):
		stack.append(tokens[0])
		#print("Adding token: %s" % tokens[0])

	grammar = get_grammar(append_tokens)
	try:
		result = grammar.parseString(expr)
	except pyparsing.ParseException as e:
		if not fail_silently:
			msg = "There was an error in your expr %s at line %s, col %s" % \
				(expr, e.lineno, e.col)
			raise ParseError(msg, expr, e.line, e.col, e.lineno)
	value = reduce_stack(stack, environment=full_environment, 
		fail_silently=fail_silently)
	return value

def is_valid(expr, environment={}):
	""" Returns True if the expr is syntatically correct and all the variables 
		exist.
	"""
	grammar = get_grammar()
	try:
		result = grammar.parseString(expr)
		for token in result:
			if re.search(VARIABLE_REGEX, token):
				if token not in environment:
					return False
	except pyparsing.ParseException as e:
		return False
	return True

def get_variables(expr):
	""" Returns a list of the variables in the expr 
	"""
	varlist = []
	grammar = get_grammar()
	try:
		result = grammar.parseString(expr)
		for token in result:
			if re.search(VARIABLE_REGEX, token):
				varlist.append(token)
	except pyparsing.ParseException as e:
		pass
	return varlist
