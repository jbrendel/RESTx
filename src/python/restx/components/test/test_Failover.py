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
from restx.components.Failover   import Failover


# ==============================
# Testing the Failover component
# ==============================

def runtest():

    #
    # -------------------------------------------------------------------
    # Mocking setup: Provide overrides for some of the component methods
    # -------------------------------------------------------------------
    #

    def new_accessResource(resource_uri, input=None, params=None, method=HTTP.GET):
        return RESOURCE_DICT[resource_uri]

    def new_httpGet(url, headers=None, timeout=None):
        # Allow client to determine return status with URLs like "..../status/200"
        STATUS_ELEM = "/status/"
        if STATUS_ELEM in url:
            i = url.find(STATUS_ELEM) + len(STATUS_ELEM)
            try:
                code = int(url[i:url.index("/", i+1)])
            except:
                code = int(url[i:])
        else:
            code = 200

        RET_ELEM = "/return/"
        if RET_ELEM in url:
            i = url.find(RET_ELEM) + len(RET_ELEM)
            try:
                ret_str = url[i:url.index("/", i+1)]
            except:
                ret_str = url[i:]
        else:
            ret_str = "Hello!"

        return code, ret_str

    def new_httpPost(url, data=None, headers=None, timeout=None):
        # Just ignoring the data
        return new_httpGet(url, headers, timeout)

    def mockit(c):
        # Perform all mocking functions on a component
        c.accessResource   = new_accessResource
        c.httpGet          = new_httpGet
        c.httpPost         = new_httpPost


    #
    # -------------------------------------------------------------------
    # The actual tests
    # -------------------------------------------------------------------
    #

    #
    # Test 1: No failover and expected return value
    #
    rctp = dict(
        site_1_uri       = "http://localhost:8091/status/200/return/foo",
        site_1_timeout   = 10,
        site_2_uri       = "",
        site_2_timeout   = 10,
        site_3_uri       = "",
        site_3_timeout   = 10,
        account_name     = "",
        account_password = "",
        expected_status  = 200,
    )
    c   = make_component(rctp, Failover)
    mockit(c)
    res = c.access(HttpMethod.GET, None)
    test_evaluator("Test 1", compare_out_str(res, 200, "foo"))

    #
    # Test 2: No failover and un-expected return value
    #
    rctp['site_1_uri'] = "http://localhost:8091/status/201/return/foo"
    c   = make_component(rctp, Failover)
    mockit(c)
    res = c.access(HttpMethod.GET, None)
    test_evaluator("Test 2", compare_out_str(res, HTTP.REQUEST_TIMEOUT, "foo"))

    #
    # Test 3: Failover because of unexpected return code
    #
    rctp['site_1_uri'] = "http://localhost:8091/status/201/return/foo"
    rctp['site_2_uri'] = "http://localhost:8091/status/200/return/bar"
    c   = make_component(rctp, Failover)
    mockit(c)
    res = c.access(HttpMethod.GET, None)
    test_evaluator("Test 3", compare_out_str(res, 200, "bar"))

    #
    # Test 4: Failover because of timeout return code
    #
    rctp['site_1_uri'] = "http://localhost:8091/status/%d/return/foo" % HTTP.REQUEST_TIMEOUT
    rctp['site_2_uri'] = "http://localhost:8091/status/200/return/bar"
    c   = make_component(rctp, Failover)
    mockit(c)
    res = c.access(HttpMethod.GET, None)
    test_evaluator("Test 4", compare_out_str(res, 200, "bar"))

    #
    # Test 5: Failover and error even on last URI
    #
    rctp['site_1_uri'] = "http://localhost:8091/status/%d/return/foo" % HTTP.REQUEST_TIMEOUT
    rctp['site_2_uri'] = "http://localhost:8091/status/201/return/bar"
    c   = make_component(rctp, Failover)
    mockit(c)
    res = c.access(HttpMethod.GET, None)
    test_evaluator("Test 5", compare_out_str(res, HTTP.REQUEST_TIMEOUT, "bar"))

    #
    # Test 6: Failover and error even on last URI, this time with POST
    #
    rctp['site_1_uri'] = "http://localhost:8091/status/%d/return/foo" % HTTP.REQUEST_TIMEOUT
    rctp['site_2_uri'] = "http://localhost:8091/status/201/return/bar"
    c   = make_component(rctp, Failover)
    mockit(c)
    res = c.access(HttpMethod.POST, None)
    test_evaluator("Test 6", compare_out_str(res, HTTP.REQUEST_TIMEOUT, "bar"))

    #
    # Test 6: Failover and expected return on last URI, this time with POST
    #
    rctp['site_1_uri'] = "http://localhost:8091/status/%d/return/foo" % HTTP.REQUEST_TIMEOUT
    rctp['site_2_uri'] = "http://localhost:8091/status/200/return/bar"
    c   = make_component(rctp, Failover)
    mockit(c)
    res = c.access(HttpMethod.POST, None)
    test_evaluator("Test 7", compare_out_str(res, 200, "bar"))

    #
    # Test 7: Failover and expected return on last URI, but with method that's not allowed
    #
    rctp['site_1_uri'] = "http://localhost:8091/status/%d/return/foo" % HTTP.REQUEST_TIMEOUT
    rctp['site_2_uri'] = "http://localhost:8091/status/200/return/bar"
    c   = make_component(rctp, Failover)
    mockit(c)
    res = c.access(HttpMethod.PUT, None)
    test_evaluator("Test 8", compare_out_str(res, HTTP.METHOD_NOT_ALLOWED, "Only supporting GET or POST for this resource"))

    return get_test_result()


