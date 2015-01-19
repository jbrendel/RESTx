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
from restx.components.Join       import Join


# ==========================
# Testing the Join component
# ==========================

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
    # Test 1: Always prefix, two matches
    #
    rctp = dict(
        keyfield_A         = "email",
        keyfield_B         = "Email",
        prefix_name_A      = "A",
        prefix_name_B      = "B",
        new_keyfield_name  = "BlahBlah",
        always_use_prefix  = True,
        resource_A_uri     = "/resource/A",
        resource_B_uri     = "/resource/B",
    )
    c = make_component(rctp, Join, MyBaseCapabilities)

    data_A = [
        { "email" : "a@b.c", "foo" : "A foo A" },
        { "email" : "b@b.c", "foo" : "A foo B" },
        { "email" : "c@b.c", "foo" : "A foo C" },
    ]
    data_B = [
        { "Email" : "x@b.c", "foo" : "B foo x", "bar" : "bar X" },
        { "Email" : "b@b.c", "foo" : "B foo b", "bar" : "bar B" },
        { "Email" : "c@b.c", "foo" : "B foo c", "bar" : "bar C" },
        { "Email" : "d@d.d", "foo" : "B foo c", "bar" : "bar C" },
    ]
    RESOURCE_DICT = { c.resource_A_uri : (200, data_A), c.resource_B_uri : (200, data_B) }

    res = c.join(None, None)
    should_be = [ {'A.foo': 'A foo C', 'B.bar': 'bar C', 'B.foo': 'B foo c', 'BlahBlah': 'c@b.c'},
                  {'A.foo': 'A foo B', 'B.bar': 'bar B', 'B.foo': 'B foo b', 'BlahBlah': 'b@b.c'} ]

    test_evaluator("Test 1", compare_out_lists(res, 200, should_be))

    #
    # Test 2: Same data, but not always prefix
    #
    rctp['always_use_prefix'] = False
    c = make_component(rctp, Join, MyBaseCapabilities)
    res = c.join(None, None)
    should_be = [ {'A.foo': 'A foo C', 'B.foo': 'B foo c', 'BlahBlah': 'c@b.c', 'bar': 'bar C'},
                  {'A.foo': 'A foo B', 'B.foo': 'B foo b', 'BlahBlah': 'b@b.c', 'bar': 'bar B'} ]

    test_evaluator("Test 2", compare_out_lists(res, 200, should_be))

    #
    # Same data, but no new keyfield name
    #
    rctp['new_keyfield_name'] = None
    c = make_component(rctp, Join, MyBaseCapabilities)
    res = c.join(None, None)
    should_be = [ {'A.foo': 'A foo C', 'B.foo': 'B foo c', 'email': 'c@b.c', 'bar': 'bar C'},
                  {'A.foo': 'A foo B', 'B.foo': 'B foo b', 'email': 'b@b.c', 'bar': 'bar B'} ]

    test_evaluator("Test 3", compare_out_lists(res, 200, should_be))

    #
    # Testing with no resulting joins
    #
    data_B[1]['Email'] = "bb@b.c"
    data_B[2]['Email'] = "cc@c.c"
    res = c.join(None, None)
    should_be = []
    test_evaluator("Test 4", compare_out_lists(res, 200, should_be))

    #
    # Testing with one input empty
    #
    data_B = dict()
    res = c.join(None, None)
    should_be = []
    test_evaluator("Test 5", compare_out_lists(res, 200, should_be))

    #
    # Testing with both inputs empty
    #
    data_A = dict()
    data_B = dict()
    res = c.join(None, None)
    should_be = []
    test_evaluator("Test 6", compare_out_lists(res, 200, should_be))

    return get_test_result()

