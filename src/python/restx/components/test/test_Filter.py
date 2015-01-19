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

# These imports are necessary for all component tests
from restx.testtools.utils       import *
from restx.components.api        import *

# Importing the component we wish to test
from restx.components.Filter     import Filter


# ============================
# Testing the Filter component
# ============================


def runtest():

    #
    # -------------------------------------------------------------------
    # Mocking setup: Provide overrides for some of the component methods
    # -------------------------------------------------------------------
    #

    class MyBaseCapabilities(BaseCapabilities):
        def accessResource(self, resource_uri, input=None, params=None, method=HTTP.GET):
            return RESOURCE_DICT[resource_uri]


    #
    # -------------------------------------------------------------------
    # The actual tests
    # -------------------------------------------------------------------
    #

    #
    # Setting up a dummy component
    #
    rctp = dict(
        input_resource_uri   = "/resource/foo",
        filter_expression_1  = "a/b/c = 123",
        filter_expression_2  = "",
        filter_expression_3  = "",
        match_all            = True,
    )
    c = make_component(rctp, Filter, MyBaseCapabilities)

    #
    # Testing filter_compile()
    #
    test_evaluator("Test 1", compare_list(c._filter_compile('a/b/c = 123'),
                                          (['a', 'b', 'c'], '=', 123)))
    test_evaluator("Test 2", compare_list(c._filter_compile('a/b/c = "123"'),
                                          (['a', 'b', 'c'], '=', '123')))
    test_evaluator("Test 3", compare_list(c._filter_compile('"a"/"one two b"/c=x  = >= true'),
                                          (['a', 'one two b', 'c=x  ='], '>=', True)))
    test_evaluator("Test 4", compare_list(c._filter_compile('"a" >= true'),
                                          (['a'], '>=', True)))
    test_evaluator("Test 5", compare_list(c._filter_compile('1 >= 123'),
                                          ([1], '>=', 123)))
    test_evaluator("Test 6", compare_list(c._filter_compile('a/1/2 >= 123'),
                                          (['a', 1, 2], '>=', 123)))
    test_evaluator("Test 7", compare_list(c._filter_compile('a/"1"/2 >= 123'),
                                          (['a', '1', 2], '>=', 123)))

    #
    # Testing element extraction
    #
    test_evaluator("Test 8",  compare_elem(123, c._get_elem([ 111, 123 ],                   c._filter_compile("1 = 1")[0])))
    test_evaluator("Test 9",  compare_elem(123, c._get_elem({ 1: 123},                      c._filter_compile("1 = 1")[0])))
    test_evaluator("Test 10", compare_elem(123, c._get_elem({ "1": 123},                    c._filter_compile('"1" = 1')[0])))
    test_evaluator("Test 11", compare_elem(1,   c._get_elem({ "1": [ 1, 2 ]},               c._filter_compile('"1"/0 = 1')[0])))
    test_evaluator("Test 12", compare_elem("a", c._get_elem({ "x": [ 1, "a" ]},             c._filter_compile('x/1 = 1')[0])))
    test_evaluator("Test 13", compare_elem("a", c._get_elem({ "x": [ 1, { "b" : "a" } ]},   c._filter_compile('x/1/b = 1')[0])))

    #
    # Testing filtering
    #
    rctp['filter_expression_1']  = "foo = xyz"
    c = make_component(rctp, Filter, MyBaseCapabilities)

    data = [
        { "email" : "a@b.c", "foo" : "abc" },
        { "blah" : 123 },
        { "email" : "b@b.c", "foo" : "xyz" },
        { "email" : "c@b.c", "foo" : "xyz" },
    ]
    RESOURCE_DICT = { c.input_resource_uri : ( 200, data ) }

    #
    # Test 14: PASS filter
    #
    res = c.filter(None, None, False)
    should_be = [
        { "email" : "b@b.c", "foo" : "xyz" },
        { "email" : "c@b.c", "foo" : "xyz" },
    ]
    test_evaluator("Test 14", compare_out_lists(res, 200, should_be))

    #
    # Test 15: Deny filter
    #
    res = c.filter(None, None, True)
    should_be = [
        { "email" : "a@b.c", "foo" : "abc" },
        { "blah" : 123 },
    ]
    test_evaluator("Test 15", compare_out_lists(res, 200, should_be))

    #
    # Test 16: Filter with dictionary at top level
    #
    c = make_component(rctp, Filter, MyBaseCapabilities)

    data = {
        "aaa" : { "email" : "a@b.c", "foo" : "abc" },
        "bbb" : { "blah" : 123 },
        "ccc" : { "email" : "b@b.c", "foo" : "xyz" },
        "ddd" : { "email" : "c@b.c", "foo" : "xyz" },
    }
    RESOURCE_DICT = { c.input_resource_uri : (200, data) }

    res = c.filter(None, None, False)
    should_be = {
        "ccc" : { "email" : "b@b.c", "foo" : "xyz" },
        "ddd" : { "email" : "c@b.c", "foo" : "xyz" },
    }
    test_evaluator("Test 16", compare_out_dicts(res, 200, should_be))

    #
    # Test 17: Other operator: !=
    #
    rctp['filter_expression_1']  = "foo != xyz"
    c = make_component(rctp, Filter, MyBaseCapabilities)

    res = c.filter(None, None, False)
    should_be = {
        "aaa" : { "email" : "a@b.c", "foo" : "abc" },
    }
    test_evaluator("Test 17", compare_out_dicts(res, 200, should_be))

    #
    # Test 18: Multiple expressions with AND
    #
    rctp['filter_expression_1']  = "b = 2"
    rctp['filter_expression_2']  = "c = 1"
    c = make_component(rctp, Filter, MyBaseCapabilities)

    data = [
        { "a" : 1, "b" : 2, "c" : 1 },
        { "a" : 1, "b" : 1, "c" : 1 },
        { "a" : 1, "b" : 2, "c" : 1 },
        { "a" : 1, "b" : 3, "c" : 1 },
        { "a" : 1, "b" : 3, "c" : 4 },
    ]
    RESOURCE_DICT = { c.input_resource_uri : (200, data) }

    res = c.filter(None, None, False)
    should_be = [
        { "a" : 1, "b" : 2, "c" : 1 },
        { "a" : 1, "b" : 2, "c" : 1 },
    ]
    test_evaluator("Test 18", compare_out_lists(res, 200, should_be))

    #
    # Test 19: Multiple expressions with OR
    #
    rctp['filter_expression_2']  = "c = 4"
    rctp['match_all']            = False
    c = make_component(rctp, Filter, MyBaseCapabilities)

    res = c.filter(None, None, False)
    should_be = [
        { "a" : 1, "b" : 2, "c" : 1 },
        { "a" : 1, "b" : 2, "c" : 1 },
        { "a" : 1, "b" : 3, "c" : 4 },
    ]
    test_evaluator("Test 19", compare_out_lists(res, 200, should_be))

    return get_test_result()

