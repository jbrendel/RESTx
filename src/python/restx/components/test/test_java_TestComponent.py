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
from restx.testtools.utils        import *
from restx.components.api         import *

# We use this method to convert output from a Java component to
# a natibe Python data structure.
from restx.languages              import languageStructToPython

# Importing the component we wish to test
from org.mulesoft.restx.component import TestComponent
from org.mulesoft.restx.parameter import ParameterDefNumberList

# Importing this one, because we need to provide a mock header for a test
from org.mulesoft.restx           import RestxHttpRequest

# Native type for numeric parameters to components or service methods
import java.math.BigDecimal


# ===============================
# Testing the Java test component
# ===============================

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
    # --------------------------------------------------------------------
    # Provide a mock for the request header. Not all components need this,
    # but one of the service methods of this component actually accesses
    # the request header.
    # --------------------------------------------------------------------
    #
    class MyRequest(RestxHttpRequest):
        def getRequestURI(self):
            return "http://foo.com"
        def getRequestHeaders(self):
            return { "foo" : [ "one", "two" ] }

    #
    # -------------------------------------------------------------------
    # The actual tests
    # -------------------------------------------------------------------
    #

    #
    # Test 1: Always prefix, two matches
    #
    rctp = dict(
        api_key         = "abcdefg",
        foo_1           = None,
        foo_2           = None,
        foo_list        = [],
        bar_list        = ParameterDefNumberList.listToArray([]),
    )

    # Create a component with our mock capabilities and request classes
    c = make_component(rctp, TestComponent, MyBaseCapabilities, MyRequest)

    res = c.foobar(HttpMethod.GET, None, "xyz", BigDecimal(10))

    # This is a Java component, so we can call the languageStructToPython() method
    # to convert the output data into a native Python structure.
    out = languageStructToPython(c, res.entity)
    data = [ u"Some text", 123,
            { u"foo" : u"This is a test", u"bar" : {
                                                      u"some ArrayList" : [ u"Blah", 12345 ],
                                                      u"some value" : 1,
                                                      u"another value" : u"Some text" } } ]

    test_evaluator("Test 1", compare_any(data, out))

    return get_test_result()

