from setuptools import setup

setup(name='yapp',
      version='0.1',
      description='Yet Another Python Parsing - a simple parser built with Pyparsing',
      url='http://github.com/jaywhy13/yapp',
      author='Jean-Mark Wright',
      author_email='jeanmark.wright@gmail.com',
      license='MIT',
      packages=['yapp'],
      install_requires = [
	    'Django>=1.5.5,<=2.0.0',
            'pyparsing>=2.0.1',
      ],
      zip_safe=False)
