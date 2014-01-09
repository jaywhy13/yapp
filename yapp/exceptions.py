class VariableMissingException(Exception):
	""" This exception occurs when a variable is missing
	"""
	def __init__(self, message, name):
		super(VariableMissingException, self).__init__(message)
		self.name = name

class ParseError(Exception):
	""" Thrown when there is a syntax error
	"""
	def __init__(self, message, expr, line, col, lineno):
		super(ParseError, self).__init__(message)
		self.line = line
		self.lineno = lineno
		self.col = col
		self.expr = expr
