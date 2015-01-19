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

"""
Commonly used helper functions when creating tests for Python components.

"""

from restx.components.base_capabilities import BaseCapabilities
from org.mulesoft.restx                 import RestxHttpRequest

class __DefaultRequest(RestxHttpRequest):
    pass

_TEST_COUNT  = 0
_TEST_FAILED = 0

# ---------------------------------
# Setup and initialization methods.
# ---------------------------------

def make_component(resource_creation_params, component_class,
                   base_capabilities_mock_class=BaseCapabilities, request_mock_class=__DefaultRequest):
    """
    Create a new component of the specified class.

    The component is initialized with the specified base-capabilities and request.

    Create a new component of the specified class and initialized
    with the provided resource-creation-time-parameters (given
    as a dict).

    With 'base_capability_mock_class' a class can be specified,
    which should derive from BaseCapabilities, but which overrides
    selected methods, for example to mock up HTTP access or access
    to other resources.

    With 'request_mock_class' a class can be specified, which should
    derive from RestxHttpRequest and which returns specific HTTP
    request headers.

    """
    c  = component_class()
    bc = base_capabilities_mock_class(c)
    c.setBaseCapabilities(bc)
    c.setRequest(request_mock_class())
    for key, value in resource_creation_params.items():
        setattr(c, key, value)
    return c


# --------------------------
# Result comparison methods.
# --------------------------

def compare_out_str(res, should_status, should_str):
    """
    Compare two strings and produce proper error message.

    A helper method that can compare the output with a 'should' output
    Used to compare string results.

    """
    if res.status != should_status:
        return "Status type is not correct.  is == %d, should == %d" % (res.status, should_status)
    is_str = res.entity
    if is_str != should_str:
        return "Wrong output strings:   is  == '%s'  should == '%s'" % (is_str, should_str)


def compare_out_lists(res, should_status, should_list):
    """
    Compare two output lists.

    A helper method that can compare the output of a resource,
    consisting of a list of things with a 'should' output.

    Used to compare list of result records.

    """
    if res.status != should_status:
        return "Status type is not correct.  is == %d, should == %d" % (res.status, should_status)
    is_list = res.entity
    # Assumes two lists of dictionaries
    if len(is_list) != len(should_list):
        return "Lists don't have the same length: is == %d, should == %d" % (len(is_list), len(should_list))
    for i, row_is in enumerate(is_list):
        row_should = should_list[i]
        if row_is.keys() != row_should.keys():
            return "Keys in rows don't match:\n    is:     %s\n    should: %s" % (row_is.keys(), row_should.keys())
        for k in row_is.keys():
            if row_is[k] != row_should[k]:
                return "Wrong value field:\n    is[%s]     == '%s'\n    should[%s] == '%s'" % (k, row_is[k], k, row_should[k])
    return None


def compare_out_dicts(res, should_status, should_dict):
    """
    Compare two output dictionaries.

    A helper method that can compare the output of a resource,
    consisting of a dictionaries of things with a 'should' output.

    Used to compare dictionaries of result records.

    """

    if res.status != should_status:
        return "Status type is not correct.  is == %d, should == %d" % (res.status, should_status)
    is_dict = res.entity
    # Assumes two dictionaries of dictionaries
    if len(is_dict) != len(should_dict):
        return "Dictionaries don't have the same length: is == %d, should == %d" % (len(is_list), len(should_list))
    for k, row_is in is_dict.items():
        row_should = should_dict[k]
        if row_is.keys() != row_should.keys():
            return "Keys in rows don't match:\n    is:     %s\n    should: %s" % (row_is.keys(), row_should.keys())
        for k in row_is.keys():
            if row_is[k] != row_should[k]:
                return "Wrong value field:\n    is[%s]     == '%s'\n    should[%s] == '%s'" % (k, row_is[k], k, row_should[k])
    return None


def compare_list(is_list, should_list):
    """
    Simply compare two iterables.

    """
    for i, elem in enumerate(is_list):
        if elem != should_list[i]:
            return "Wrong value field:   is[%d] == '%s'   should[%d] == '%s'" % (i, elem, i, should_list[i])
    return None

def compare_elem(is_elem, should_elem):
    """
    Compare a single element.

    """
    if type(should_elem) != type(is_elem):
        return "Wrong element type:   is == '%s'   should == '%s'\n    is-value ==     '%s'\n    should-value == '%s')" % (type(is_elem), type(should_elem), is_elem, should_elem)
    if is_elem != should_elem:
        return "Wrong element value:  is == '%s'   should == '%s'" % (is_elem, should_elem)
    return None

def compare_any(should_obj, is_obj):
    """
    Compare two parameter definition dictionaries.

    """
    if type(should_obj) != type(is_obj):
        return "Object type '%s' encountered, when expecting type '%s'" % (type(is_obj), type(should_obj))

    if len(should_obj) != len(is_obj):
        return "Object has length %d, when expecting length %d" % (len(is_obj), len(should_obj))

    if type(is_obj) is list:
        for i, is_elem in enumerate(is_obj):
            should_elem = should_obj[i]
            if type(is_elem) in [ list, dict ]:
                m = compare_any(should_elem, is_elem)
            else:
                m = compare_elem(is_elem, should_elem)
            if m:
                return m

    elif type(is_obj) is dict:
        for key in is_obj:
            is_elem = is_obj[key]
            if key not in should_obj:
                return "Expected key '%s' not found in data" % key
            should_elem = should_obj[key]
            if type(is_elem) in [ list, dict ]:
                m = compare_any(should_elem, is_elem)
            else:
                m = compare_elem(is_elem, should_elem)
            if m:
                return m

    return None


# ------------------------------------
# Evaluate test result and keep stats.
# ------------------------------------

def test_evaluator(test_name, out):
    """
    Check the supplied result, print message and update stats.

    """
    global _TEST_COUNT, _TEST_FAILED
    # Prints test results in a nice manner
    _TEST_COUNT += 1
    if out:
        print "*** %s: Error: %s" % (test_name, out)
        _TEST_FAILED += 1
    else:
        print "--- %s: Success!" % test_name


# --------------------------------------------------------------------------
# Test running methods (used by the test framework, not by the test author).
# --------------------------------------------------------------------------
def init_test_run():
    global _TEST_COUNT, _TEST_FAILED
    _TEST_COUNT  = 0
    _TEST_FAILED = 0

def get_test_result():
    return ( _TEST_FAILED, _TEST_COUNT )

