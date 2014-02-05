from django.test import TestCase

from yapp import *
from yapp.exceptions import *

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

        tests = ["'a'", "2", "x", "y", "-4", "2.13", "2.", "2 ^ 13", "2 * 4", "4 /2",
	         "4 * 3", "5.34 * 3", "3.4 + 1", "2+3+4", "(2+3)", "2 + (3 * 4)", "2 * 3.0"]
        for test in tests:
	    	# these should give no errors
    		stack[:] = []
    		result = get_grammar().parseString(test)
    		value = parse(test, fail_silently=True)
    		if not re.search("[a-zA-Z]+", test):
    			test = test.replace("^", "**")
    			self.assertEquals(value, eval(test))
    		#print("Stack after: %s = %s, result = %s" % (test, stack, result))

        # Start testing functions
        environment = {
            "foo" : lambda : 2,
            "times2" : lambda x : x*2,
            "minus" : lambda x,y: x-y,
            "minus3" : lambda x,y,z : x-y-z,
            "x" : 2,
            "abool" : True
        }
        self.assertEqual(parse("foo()", environment), 2)
        self.assertEqual(parse("times2(2)", environment), 4)
        self.assertEqual(parse("minus(5,2)", environment), 3)
        self.assertEqual(parse("minus(5*5,2*2)", environment), 21)
        self.assertEqual(parse("minus3(10,5,2)", environment), 3)
        self.assertEqual(parse("x * 3", environment), 6)
        self.assertEqual(parse("3 * x", environment), 6)
        self.assertEqual(parse("x ^ 3", environment), 8)
        self.assertEqual(parse("x < 3", environment), True)
        self.assertEqual(parse("x > 3", environment), False)

        # test variables required
        self.assertEqual(["x"], get_variables("x > 3"))

        # test validity checking
        self.assertTrue(is_valid("x * 2", environment))
        self.assertFalse(is_valid("x * 2")) # no env
        self.assertFalse(is_valid("x * ", environment))

        # test syntax error exception
        with self.assertRaises(ParseError):
            parse("2 / ", fail_silently=False)

        # test syntax error exception
        with self.assertRaises(VariableMissingException):
            parse("x * 2 ", fail_silently=False)

        # test booleans
        self.assertTrue(parse("abool", environment))
        self.assertFalse(parse("not(abool)", environment))

        # test strings
        self.assertTrue(parse("eq('hello', 'hello')"))
        self.assertEqual(parse("'hello'"), "hello")

        strs = ["this is a long string 12356&*#@$)("]
        for s in strs:
            self.assertEqual(parse("'%s'" % s), s)

        # test lists
        self.assertFalse(parse("in(1, [2,3,4])"))
        self.assertTrue(parse("in(2, [2,3,4])"))
        self.assertTrue(parse("in('a', ['a','b','c'])"))
        self.assertFalse(parse("in('d', ['a','b','c'])"))
