#!/usr/bin/env python
# $Id: Tests.py,v 1.2 2001/06/18 17:26:01 tavis_rudd Exp $
"""Unit-testing framework for the Cheetah package

TODO
================================================================================
- Check NameMapper independently


Meta-Data
================================================================================
Author: Tavis Rudd <tavis@calrudd.com>,
License: This software is released for unlimited distribution under the
         terms of the Python license.
Version: $Revision: 1.2 $
Start Date: 2001/03/30
Last Revision Date: $Date: 2001/06/18 17:26:01 $
"""
__author__ = "Tavis Rudd <tavis@calrudd.com>"
__version__ = "$Revision: 1.2 $"[11:-2]


##################################################
## DEPENDENCIES ##

import sys
import types                      
import re
from copy import deepcopy
import os.path


try:
    import unittest
except:
    import unittest_local_copy as unittest

# intra-package imports ...
import NameMapper as NameMapper
from Template import Template
from Delimeters import delimeters

##################################################
## CONSTANTS & GLOBALS ##

True = (1==1)
False = (0==1)


##################################################
## TEST CLASSES ##

class AbstractTestCase(unittest.TestCase):
    def nameSpace(self):
        return self._nameSpace
       
    def __init__(self, title, template, expectedOutput, nameSpace):
        self.testTitle = title
        self.template = template
        self.expectedOutput = expectedOutput
        self._nameSpace = nameSpace
        unittest.TestCase.__init__(self, "runTest")

class VerifyTemplateOutput(AbstractTestCase):          
    def runTest(self):
        servlet = Template(self.template, self.nameSpace())
        output = servlet.respond()

        assert output == self.expectedOutput, \
               ('Template output mismatch\n\tTest Title: ' + self.testTitle + 
                '\n\tInput Template = %(template)s\n\tExpected Output = ' + 
                '%(expected)s---\n\tActual Output = %(actual)s---\n' ) \
               % {'template':self.template, 'expected':self.expectedOutput,
                  'actual':output}


##################################################
## TEST DATA FOR USE IN THE TEMPLATES ##

class DummyClass:
    def __str__(self):
        return 'object'
        
    def meth(self, arg="arff"):
        return str(arg)

    def meth1(self, arg="doo"):
        return arg

    def meth2(self, arg1="a1", arg2="a2"):
        return str(arg1) + str(arg2)

def dummyFunc(arg="Scooby"):
    return arg

defaultTestNameSpace = {
    'numOne': 1,
    'numTwo': 2,
    'c':"blarg",
    'numFive':5,
    'emptyString':'',
    'numZero':0,
    'func':dummyFunc,
    'meth':DummyClass().meth1,
    'obj':DummyClass(),
    'dict':{'one':'item1',
            'two':'item2',
            'nestedDict':{1:'nestedItem1',
                          'two':'nestedItem2'
                          },
            'nestedFunc':dummyFunc,
            },
    'dict2': {'one':'item1', 'two':'item2'},
    'blockToBeParsed':"""$numOne $numTwo""",
    }


##################################################
## TEST CASES ##


# combo tests
# negative test cases for expected exceptions
# black-box vs clear-box testing
# do some tests that run the Template for long enough to check that the refresh code works

## [testTitle, template, expected output]

posixCases = [
    ['single $var','$c','blarg'],
    ['simple $var permutations',
     """
$ $500 $. \$var
'''
$emptyString $numZero
${numOne}$numTwo
$numOne and $numTwo $c. $dict.one $dict.nestedFunc
$func $func. $func(). $func(4). $func('x'). $func("x"). $func("x"*2). $func(arg="x"). $func(arg='x').
$meth $meth. $meth(). $meth(5). $meth('y'). $meth("y"). $meth("y"*2). $meth(arg="y"). $meth(arg='y').
$obj $obj.
$obj.meth $obj.meth. $obj.meth(). $obj.meth(6).
$obj.meth('z'). $obj.meth("z"). $obj.meth("z"*2). $obj.meth(arg="z"). $obj.meth(arg='z').""",
     
     """
$ $500 $. $var
'''
 0
12
1 and 2 blarg. item1 Scooby
Scooby Scooby. Scooby. 4. x. x. xx. x. x.
doo doo. doo. 5. y. y. yy. y. y.
object object.
arff arff. arff. 6.
z. z. zz. z. z."""
              ],
    
    ]


standardVarRegex = re.compile(r"(?:(?<=\A)|(?<!\\))\$((?:\*|(?:\*[0-9\.]*\*)){0,1}" +
                                     r"[A-Za-z_](?:[A-Za-z0-9_\.]*[A-Za-z0-9_]+)*" +
                                     r"(?:\(.*?\))*)", re.DOTALL)

def convertVars(titlePrefix, replacementString, caseData):
     caseData = deepcopy(caseData)
     caseData[0] = titlePrefix + caseData[0]
     caseData[1] = standardVarRegex.sub(replacementString, caseData[1])
     return caseData

for i in range(len(posixCases)):
    posixCases.append(convertVars("Braced cached ${vars} : ", r"${\1}", posixCases[i] ))
    posixCases.append(convertVars("Dynamic $*vars : ", r"$*\1", posixCases[i] ))
    posixCases.append(convertVars("Braced Dynamic ${*vars} : ", r"${*\1}", posixCases[i] ))
    posixCases.append(convertVars("Dynamic Refresh $*15*vars : ", r"$*15*\1", posixCases[i] ))
    posixCases.append(convertVars("Braced Dynamic Refresh ${*15*vars} : ", r"${*15*\1}", posixCases[i] ))



nestedVarTests = [
    ['$var($var)',
     """$func($numOne) $meth($numOne) $obj.meth($numOne)""",
     '1 1 1'],
    ['$var($var)',
     """${func($numOne)} ${meth($numOne)} ${obj.meth($numOne)}""",
     '1 1 1'],
    ]
posixCases += nestedVarTests

commentTests = [
    ['simple ## comment - with whitespace - should gobble',
     "  ##  \n",
     "",],

    ['simple ## comment - no whitespace',
     "##",
     "",],

    ['simple ## comment - after other text',
     "\nblarg ## foo",
     "\nblarg ",],

    ['simple ## comment - with #if directive',
     "##if 0\nblarg\n##end if\n",
     "blarg\n",],
    
    ['simple #* comment *# - no whitespace',
     "#* \naoeuaoeu\naoeuaoeu\n *#",
     "",],

    ['simple #* comment *# - with whitespace',
     "\n#* \naoeuaoeu\naoeuaoeu\n *#  ",
     "\n  ",],
    ]
posixCases += commentTests

forLoopTests = [
    ['simple #for loop',
     """#for $i in range(5)\n$i\n#end for\n""",
     """0\n1\n2\n3\n4\n""",],
    ['simple #for loop with no whitespace at the end',
     """#for $i in range(5)\n$i\n#end for""",
     """0\n1\n2\n3\n4\n""",],
    ['simple #for loop with no whitespace',
     """#for $i in range(5)\n$i#end for""",
     """01234""",],
    ['simple #for loop with explicit closures',
     """#for $i in range(5)/#$i#end for/#""",
     """01234""",],
    
    ['simple #for loop using another $var',
     """#for $i in range($numFive)\n$i\n#end for\n""",
     """0\n1\n2\n3\n4\n""",],

    ['simple #for loop using $dict2',
     """#for $key, $val in $dict2.items\n$key - $val\n#end for\n""",
     """one - item1\ntwo - item2\n""",],
    ['simple #for loop using $dict2, with $ on $key,$val',
     """#for key, val in $dict2.items\n$key - $val\n#end for\n""",
     """one - item1\ntwo - item2\n""",],
    
    ['simple #for loop using $dict2 and another $var ($c)',
     "#for $key, $val in $dict2.items\n$key - $val - $c\n#end for\n",
     "one - item1 - blarg\ntwo - item2 - blarg\n",],
    ['simple #for loop using $dict2 and another $*var ($*c)',
     "#for $key, $val in $dict2.items\n$key - $val - $*c\n#end for\n",
     "one - item1 - blarg\ntwo - item2 - blarg\n",],
    ['simple #for loop using $dict2 and another $*15*var ($*15*c)',
     "#for $key, $val in $dict2.items\n$key - $val - $*15*c\n#end for\n",
     "one - item1 - blarg\ntwo - item2 - blarg\n",],

    ['simple #for loop using $dict2 and a method of the local var',
     "#for $key, $val in $dict2.items\n$key - $val.upper\n#end for\n",
     "one - ITEM1\ntwo - ITEM2\n",],
    ]
posixCases += forLoopTests


ifBlockTests = [
    ['simple #if block',
     "#if 1\n$c\n#end if\n",
     "blarg\n",],

    ['simple #if block with no trailing whitespace',
     "#if 1\n$c\n#end if",
     "blarg\n",],

    ['simple #if block with explicit closures',
     "#if 1/#$c#end if/#",
     "blarg",],
    
    ['simple #if block using $numOne',
     "#if $numOne\n$c\n#end if\n",
     "blarg\n",],
    
    ['simple #if block using a $numZero',
     "#if $numZero\n$c\n#end if\n",
     "",],

    ['simple #if block using a $emptyString',
     "#if $emptyString\n$c\n#end if\n",
     "",],

    ['simple #if... #else ... block using a $emptyString',
     "#if $emptyString\n$c\n#else\n$c - $c#end if\n",
     "blarg - blarg",],

    ['simple #if... #elif ... #else ... block using a $emptyString',
     "#if $emptyString\n$c\n#elif $numOne\n$numOne\n#else\n$c - $c#end if\n",
     "1\n",],

    ['simple "#if not" test',
     "#if not $emptyString\n$c\n#elif $numOne\n$numOne\n#else\n$c - $c#end if\n",
     "blarg\n",],

    ['simple #if block using a $*emptyString',
     "#if $*emptyString\n$c\n#end if\n",
     "",],
    
    ]
posixCases += ifBlockTests

blockTests = [
    ['simple #block - with no whitespace',
     "#block testBlock\nthis is a\ntest block\n#end block testBlock\n",
     "this is a\ntest block\n",],

    ['simple #block - with whitespace - should gobble',
     "  #block testBlock\nthis is a\ntest block\n  #end block testBlock\n",
     "this is a\ntest block\n",],

    ['simple #block - with explicit closures',
     "#block testBlock/#this is a\ntest block#end block testBlock/#\n",
     "this is a\ntest block\n",],

    ['#block - with explicit closures and surrounding whitespace',
     "  #block testBlock/#this is a\ntest block#end block testBlock/#  \n",
     "  this is a\ntest block  \n",],

    ['#block - long block test',
     '#block longBlock\n' + ' aoeu  aoeu   aoeu   aoeuoae ao uaoeu aoeu aoeu\n'*2000 +
     '#end block longBlock',
     ' aoeu  aoeu   aoeu   aoeuoae ao uaoeu aoeu aoeu\n'*2000,],


    ]
posixCases += blockTests


macroTests = [
    ['simple #macro - with no whitespace',
     "#macro testMacro()\nthis is a\ntest block\n#end macro",
     "",],
    ['simple #macro + call - with no whitespace',
     "#macro testMacro()\nthis is a\ntest block\n#end macro\n#testMacro()",
     "this is a\ntest block",],

    ['simple #macro - with whitespace - should gobble',
     "  #macro testMacro()\nthis is a\ntest block\n#end macro  ",
     "",],

    ['simple #macro + call - with whitespace - should gobble',
     "  #macro testMacro()\nthis is a\ntest block\n#end macro  \n#testMacro()",
     "this is a\ntest block",],

    ['simple #macro + call - with an arg',
     "#macro testMacro(a=1234)\nthis is a\ntest block $a\n#end macro\n#testMacro()",
     "this is a\ntest block 1234",],

    ['simple #macro + call - with an arg, using arg in call',
     "#macro testMacro(a=1234)\nthis is a\ntest block $a\n#end macro\n#testMacro(9876)",
     "this is a\ntest block 9876",],

    ['simple #macro + call - with two args, using one',
     """#macro testMacro(a=1234, b='blarg')\nthis is a\ntest block $a $b\n#end macro\n#testMacro(9876)""",
     "this is a\ntest block 9876 blarg",],

    ['simple #macro + call - with two args, using both',
     """#macro testMacro(a=1234, b='blarg')\nthis is a\ntest block $a $b\n#end macro\n#testMacro(5,$numOne)""",
     "this is a\ntest block 5 1",],

    ]
posixCases += macroTests


setTests = [
    ['simple #set',
     "#set $testVar = 'blarg'",
     "",],

    ['simple #set - with no whitespace',
     "#set $testVar='blarg'",
     "",],

    ['simple #set + use of var',
     "#set $testVar = 'blarg'\n$testVar",
     "blarg",],

    ['#set with a dictionary',
     """#set $testDict = {"one":"one1","two":"two2","three":"three3"}
$testDict.one
$testDict.two""",
     """one1
two2""",],


    ['#set with string, then used in #if block',
     """#set $test='a string'
#if $test/#blarg#end if""",
     "blarg",],

    ]

posixCases += setTests


rawTests = [
    ['simple #raw - with no whitespace',
     "#raw",
     "",],

    ['#raw followed by $vars',
     "#raw\n$varName1 $varName2",
     "$varName1 $varName2",],

    ['#raw followed by $vars, and preceeded by real $vars',
     "$numOne\n#raw\n$varName1 $varName2",
     "1\n$varName1 $varName2",],

    ['#raw and #end raw surrounded by real $vars',
     "$numOne\n#raw\n$varName1 $varName2\n#end raw\n$numTwo",
     "1\n$varName1 $varName2\n2",],

    ]
posixCases += rawTests

includeTests = [
    ['simple #include of $emptyString - with no whitespace',
     "#include $emptyString",
     "",],

    ['simple #include of $blockToBeParsed - with no whitespace',
     "#include $blockToBeParsed",
     "1 2",],

    ['simple #include of $blockToBeParsed - with whitespace',
     "\n#include $blockToBeParsed\n",
     "\n1 2",],

    ['simple #include of file - with no whitespace',
     "#include 'parseTest.txt'",
     "1 2",],

    ['simple #include of file - with whitespace',
     "#include  'parseTest.txt'",
     "1 2",],

    ]
posixCases += includeTests


includeRawTests = [
    ['simple #include raw of $emptyString - with no whitespace',
     "#include raw $emptyString",
     "",],

    ['simple #include raw of $blockToBeParsed - with no whitespace',
     "#include raw $blockToBeParsed",
     "$numOne $numTwo",],

    ['simple #include raw of file - with no whitespace',
     "#include raw 'parseTest.txt'",
     "$numOne $numTwo",],

    ['simple #include raw of file - with whitespace',
     "#include raw  'parseTest.txt'",
     "$numOne $numTwo",],

    ]
posixCases += includeRawTests

callMacroTests = [

    ['simple #macro + explicit #callMacro call',
     """#macro testMacro(a=1234, b='blarg',c='argC')
this is a
test block $a $b $c
#end macro
#callMacro testMacro(a=9876)
#arg b
joe
#end arg

#arg c
bloggs
#end arg

#end callMacro
""",
     "this is a\ntest block 9876 joe bloggs",],
    
    ]
posixCases += callMacroTests


#extendTests = [
#    ['simple #extend - with no whitespace',
#     "#extend Cheetah.Templates.SkeletonPage",
#     "",],
#    ]
#posixCases += extendTests
# @@ at the moment the #entend directive is only caught by Servlet.extendTemplate()



windowsCases = deepcopy(posixCases)
for case in windowsCases:
    case[1] = case[1].replace("\n","\r\n")
    case[2] = case[2].replace("\n","\r\n")

# the dataDirectiveTests must be added after the windows line ending conversion 
# as \r\n appears to be an invalid line ending for python code chunks that are
# exec'd on Posix systems

dataDirectiveTests = [
    ['simple #data block + use of the vars that are assigned',
     """#data
testVar = 1234
testVar2 = 'aoeu'
#end data
$testVar
$testVar2
""",
     "1234\naoeu\n",],
    ]
posixCases += dataDirectiveTests

suiteData = [
    ['posixCases', posixCases],
    ['windowsCases', windowsCases],
    ]


def buildTestSuite(suiteTitle, testCasesData):
    suite = unittest.TestSuite()
    for testData in testCasesData:
        suite.addTest( VerifyTemplateOutput(
            suiteTitle + ": " + testData[0], testData[1], testData[2], defaultTestNameSpace) )
    return suite

def allSuites():
    suitesList = []
    for testSuite in suiteData:
        suitesList.append( buildTestSuite(testSuite[0], testSuite[1]) )
        
    return unittest.TestSuite(suitesList)

def runTests():
    runner = unittest.TextTestRunner(stream=sys.stdout)
    unittest.main(defaultTest='allSuites', testRunner=runner)

##################################################
## if run from the command line ##
if __name__ == '__main__':
    if not os.path.exists('parseTest.txt'):
        fp = open('parseTest.txt','w')
        fp.write("$numOne $numTwo")
        fp.flush()
        fp.close
    runTests()

