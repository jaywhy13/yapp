from django.test import TestCase

from yapp import *

class YappTest(TestCase):
    def test_yapp(self):
        """
        """
        # Test variables
        indents = ["x", "x1", "x_1"]
        for var in indents:
        	self.assertIn(var, ident.parseString(var)[0])

        # Test numbers (ints and floats)
        nums = range(-10, 10)
        for num in nums:
        	self.assertIn(str(num), integer.parseString(str(num))[0])

        nums = [1.012 * x for x in range(-10, 10)]
        for num in nums:
        	self.assertIn(str(num), decimal.parseString(str(num))[0])

        tests = ["2", "x", "y", "-4", "2.13", "2.", "2 ^ 13", "2 * 4", "4 /2",
	         "4 * 3", "5.34 * 3", "3.4 + 1", "2+3+4", "(2+3)", "2 + (3 * 4)"]
        for test in tests:
	    	# these should give no errors
    		stack[:] = []
    		result = get_grammar().parseString(test)
    		value = evaluate(test)
    		if not re.search("[a-zA-Z]+", test):
    			test = test.replace("^", "**")
    			self.assertEquals(value, eval(test))
    		#print("Stack after: %s = %s, result = %s" % (test, stack, result))







