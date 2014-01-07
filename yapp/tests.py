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
    		value = parse(test)
    		if not re.search("[a-zA-Z]+", test):
    			test = test.replace("^", "**")
    			self.assertEquals(value, eval(test))
    		#print("Stack after: %s = %s, result = %s" % (test, stack, result))

        # Start testing functions
        environment = {
            "foo" : lambda : 2,
            "times2" : lambda x : x*2,
            "minus" : lambda x,y: x-y,
            "minus3" : lambda x,y,z : x-y-z
        }
        self.assertEqual(parse("foo()", environment), 2)
        self.assertEqual(parse("times2(2)", environment), 4)
        self.assertEqual(parse("minus(5,2)", environment), 3)
        self.assertEqual(parse("minus(5*5,2*2)", environment), 21)
        self.assertEqual(parse("minus3(10,5,2)", environment), 3)
