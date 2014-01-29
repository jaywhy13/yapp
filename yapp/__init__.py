import re
import inspect
import types

from pyparsing import (
	Word, Literal, alphas, alphanums, nums, Optional,
	delimitedList, Group,
	Combine,
	StringEnd,
	ZeroOrMore,
	Forward,
	sglQuotedString
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
decimal = Combine(integer + point + Optional(number))

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
lbracket = Literal("[")
rbracket = Literal("]")

stack = []

def get_grammar(save_token_function=lambda: None,
		save_int_function=lambda: None,
		save_decimal_function=lambda: None,
		save_string_function=lambda: None,
		save_ident_function=lambda: None,
		save_list_function=lambda: None,
	):
	expr = Forward()
	atom = Forward()
	arg = expr
	args = delimitedList(arg)

	func_call = (ident + lbrace + Optional(args) + rbrace).setParseAction(save_token_function)

	bracketed_list = (lbracket + Optional(delimitedList(atom)) + rbracket).setParseAction(save_list_function)

	atom << ( bracketed_list | func_call | (lbrace + expr.suppress() + rbrace)  | ( decimal.setParseAction(save_decimal_function) | integer.setParseAction(save_int_function) | ident.setParseAction(save_ident_function) | sglQuotedString.setParseAction(save_string_function) ))

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
	">" : lambda a,b : a > b,
	"<" : lambda a,b : a < b,
	">=" : lambda a,b : a >= b,
	"<=" : lambda a,b : a <= b,
}


function_map = {
	"not" : lambda x: not x,
	"eq" : lambda x,y : x == y,
	"in" : lambda x,y : x in y,
}

VARIABLE_REGEX = '^[a-zA-Z][a-zA-Z0-9_]*$'

def reduce_stack(stack, environment={}, fail_silently=True):
	""" Reduces what's currently on the stack to a value
	"""
	op = stack.pop()
	if str(op).startswith("'") and str(op).endswith("'"):
		return op[1:-1] # remove the quotes
	elif str(op).startswith("["):
		l = []
		op = op[1:-1]
		list_len = len(op)
		for i in range(list_len):
			l.append(stack.pop())
		l.reverse()
		return l
	elif op in op_map.keys():
		op2 = reduce_stack(stack, environment, fail_silently)
		op1 = reduce_stack(stack, environment, fail_silently)
		return op_map[op](op1, op2)
	elif re.search(VARIABLE_REGEX, str(op)):
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
	return op

def parse(expr, environment={}, fail_silently=True):
	full_environment = function_map.copy()
	full_environment.update(environment)
	stack = []
	def append_tokens(s, l, tokens):
		stack.append(tokens[0])
		#print(" + Adding token: %s from tokens: %s" % (tokens[0], tokens))

	def convert_int(s, l, tokens):
		stack.append(int(tokens[0]))

	def convert_decimal(s, l, tokens):
		stack.append(float(tokens[0]))

	def convert_string(s, l, tokens):
		stack.append(tokens[0][1:-1])

	def append_list(s, l, tokens):
		stack.append(tokens)

	grammar = get_grammar(
		append_tokens, 
		convert_int,
		convert_decimal,
		convert_string,
		append_tokens,
		append_list)

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
