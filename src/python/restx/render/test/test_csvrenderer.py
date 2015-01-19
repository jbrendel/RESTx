"""
RESTx: Sane, simple and effective data publishing and integration. 

Copyright (C) 2010   MuleSoft Inc.    http://www.mulesoft.com

This program is free software: you can redistribute it and/or modify 
it under the terms of the GNU General Public License as published by 
the Free Software Foundation, either version 3 of the License, or 
(at your option) any later version. 

This program is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
GNU General Public License for more details. 

You should have received a copy of the GNU General Public License 
along with this program.  If not, see <http://www.gnu.org/licenses/>. 

"""

#
# To run this and other RESTx test files, use bin/testrun.
#

# This needs to be imported by all tests
from restx.testtools.utils  import *

# Importing the code we wish to test
from restx.render           import CsvRenderer


# ==================================
# Testing the CSV renderer component
# ==================================

def runtest():

    r = CsvRenderer()

    #
    # Test 1: Basic output of lists
    #
    data   = [ [ 1, 2, 3 ], [ "a", "b", "c" ] ]
    should = "column_1;column_2;column_3\n1;2;3\na;b;c\n"
    res    = r.render(data)
    test_evaluator("Test 1", compare_elem(res, should))

    #
    # Test 2: Basic output of lists
    #
    data   = [ [ 1, 2, 3 ], [ "a", "b", "c", "d" ] ]
    should = "column_1;column_2;column_3\n1;2;3\na;b;c;d\n"
    res    = r.render(data)
    test_evaluator("Test 2", compare_elem(res, should))

    #
    # Test 3: Basic output of lists
    #
    data   = [ [ 1, 2, 3, 4 ], [ "a", "b", "c" ] ]
    should = "column_1;column_2;column_3;column_4\n1;2;3;4\na;b;c\n"
    res    = r.render(data)
    test_evaluator("Test 3", compare_elem(res, should))

    #
    # Test 4: Column labels determined by dictionary
    #
    data   = [ { "a":11, "b":22, "c":33 }, { "foo" : "abc", "b" : 222, "xyz" : 123 } ]
    should = "a;b;c\n11;22;33\n;222;\n"
    res    = r.render(data)
    test_evaluator("Test 4", compare_elem(res, should))


    return get_test_result()



