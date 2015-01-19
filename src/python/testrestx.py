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
# Run this one with Jython
#

import sys
#import restxjson as json
import json
import time
import types
import string
import urllib
import datetime

#from restx.core.parameter import *

import snap_http_lib as http   # A decent URL library

SERVER_URL = "http://localhost:8001"
DOCROOT = ""
#SERVER_URL = "http://localhost:8080/restx"
#DOCROOT = "/restx"


TEST_RESOURCES = []

def _pretty_json(obj):
    """
    Output an object as pretty-printed JSON.

    """
    return json.dumps(obj, indent=4)

def _get_data(relative_url):
    """
    Helper method accesses a URL on the server and returns the data (interprets the JSON).

    @param relative_url: The relative URL on the server. A starting slash may be
                         specified, but either way, it's always interpreted to be
                         relative to "/".
    @type  relative_url: string

    @return:             The JSON interpreted data and the response object as a tuple.
    @rtype               tuple

    """
    if DOCROOT:
        if relative_url.startswith(DOCROOT):
            relative_url = relative_url[len(DOCROOT):]
    if relative_url.startswith("/"):
        relative_url = relative_url[1:]
    resp = http.urlopen("GET", SERVER_URL + "/" + relative_url, headers={"Accept" : "application/json"})
    buf = resp.read()
    if resp.getStatus() == 200:
        data = json.loads(buf)
    else:
        data = buf
    return (data, resp)

def _send_data(relative_url, obj):
    """
    Helper method that POSTs an object to URL as JSON.

    @param relative_url: The relative URL on the server. A starting slash may be
                         specified, but either way, it's always interpreted to be
                         relative to "/".
    @type  relative_url: string

    @param obj:          The object to be parsed to JSON and sent.
    @type obj:           object

    @return:             The JSON interpreted data and the response object as a tuple.
    @rtype               tuple

    """
    if DOCROOT:
        if relative_url.startswith(DOCROOT):
            relative_url = relative_url[len(DOCROOT):]
    if relative_url.startswith("/"):
        relative_url = relative_url[1:]
    resp = http.urlopen("POST", SERVER_URL + "/" + relative_url, headers={"Accept" : "application/json", "Content-type" : "application/json" }, data=json.dumps(obj))
    buf = resp.read()
    if resp.getStatus() >= 200 and resp.getStatus() <= 300:
        data = json.loads(buf)
    else:
        data = buf
    return (data, resp)


def _delete(relative_url):
    """
    Helper method that sends a DELETE message to the server.

    @param relative_url: The relative URL on the server. A starting slash may be
                         specified, but either way, it's always interpreted to be
                         relative to "/".
    @type  relative_url: string

    @return:             The JSON interpreted data and the response object as a tuple.
    @rtype               tuple

    """
    if DOCROOT:
        if relative_url.startswith(DOCROOT):
            relative_url = relative_url[len(DOCROOT):]
    if relative_url.startswith("/"):
        relative_url = relative_url[1:]
    resp = http.urlopen("DELETE", SERVER_URL + "/" + relative_url)
    buf = resp.read()
    return buf, resp


def _dict_compare(should_pdef, is_pdef):
    """
    Compare two parameter definition dictionaries.

    """
    assert(type(should_pdef) is dict)
    assert(type(is_pdef) is dict)
    assert(len(should_pdef) == len(is_pdef))

    for name in should_pdef:
        assert(name in is_pdef)
        if type(should_pdef[name]) is dict:
            _dict_compare(should_pdef[name], is_pdef[name])
        else:
            assert(should_pdef[name] == is_pdef[name])


# -------------------------------------------------------------------------------------------------------------------------
# Test methods
# -------------------------------------------------------------------------------------------------------------------------
def test_10_home():
    """
    Test that the home URL returns the expected data.

    """
    actual, resp = _get_data("/")
    assert(resp.getStatus() == 200)

    should = {
                    "code"     : DOCROOT + "/code",
                    "resource" : DOCROOT + "/resource",
                    "specialized code" : DOCROOT + "/specialized",
                    "doc"      : DOCROOT + "/meta/doc",
                    "static"   : DOCROOT + "/static",
                    "name"     : "MuleSoft RESTx server",
                    "version"  : "0.9.4"
             }
    allkeys = [ 'code', 'resource', 'doc', 'static', 'name', 'version', 'specialized code' ]

    for name in should:
        assert(name in actual)
        assert(actual[name] == should[name])

    for name in actual:
        assert(name in allkeys)


def test_14_not_found():
    """
    Test that the documentation can be received.

    """
    wrong_urls = [ "/sldkfjhadlskjhsdal", "/resource/alkdsjfhaljkdha", "/meta/asdkslakdhlhksa", "/code/aljkdhaljkdhfadlkf", "/static" ]
    for url in wrong_urls:
        data, resp = _get_data(url)
        assert(resp.getStatus() == 404)


def test_18_meta_doc():
    """
    Test that the documentation can be received.

    """
    data, resp = _get_data("/meta/doc")
    assert(resp.getStatus() == 200)
    assert("Welcome to RESTx!" in data)


def test_30_code():
    """
    Test that information about the installed components is returned correctly.

    """
    data, resp = _get_data("/code")
    assert(resp.getStatus() == 200)

    # We expect to see at least the TwitterComponent
    assert("TwitterComponent" in data)

    # Each entry here should have a 'desc' and 'uri' field.
    for name, cdef in data.items():
        # Make sure they contain all the mandatory fields...
        assert("desc" in cdef)
        assert("uri" in cdef)
        # ... and nothing more than that
        for k in cdef:
            assert(k in [ 'desc', 'uri' ])


def test_40_twitter_code():
    """
    Test that information returned about the Twitter component is correct.

    """
    cdef, resp = _get_data("/code/TwitterComponent")

    assert(resp.getStatus() == 200)

    expected_keys = [ "desc", "doc", "name", "params", "resource_creation_params", "services", "uri" ]
    for name in expected_keys:
        assert(name in cdef)
    assert(len(expected_keys) == len(cdef))
    assert(cdef['name'] == "TwitterComponent")
    assert(cdef['uri']  == DOCROOT + "/code/TwitterComponent")
    assert(cdef['desc'] == "Provides access to a Twitter account.")
    assert(cdef['doc']  == DOCROOT + "/code/TwitterComponent/doc")

    params_def = {
        "account_name": {
            "desc": "Twitter account name", 
            "required": True, 
            "type": "string"
        }, 
        "account_password": {
            "desc": "Password", 
            "required": True, 
            "type": "password"
        }
    } 

    _dict_compare(cdef['params'], params_def)

    resource_creation_params_def = {
        "desc": {
            "default": "A 'TwitterComponent' resource", 
            "desc": "Specifies a description for this new resource", 
            "required": False, 
            "type": "string"
        }, 
        "suggested_name": {
            "desc": "Can be used to suggest the resource name to the server", 
            "required": True, 
            "type": "string"
        },
        'specialized': {
            'desc': 'Specifies if we want to create a specialized component resource (true) or a normal resource (false)',
            'type': 'boolean',
            'required': False,
            'default': False
        }
    } 

    _dict_compare(cdef['resource_creation_params'], resource_creation_params_def)

    services_def = {
        u'status': {
            u'desc': u'You can GET the status or POST a new status to it.',
            u'uri': u'/code/TwitterComponent/status',
            u'output_types': [u'application/json', u'application/xml', u'text/html', u'*/*' ],
            u'input_types': [u'application/json', u'application/x-www-form-urlencoded'],
        },
        u'home_timeline': {
            u'desc': u'You can GET the home timeline of the user.',
            u'output_types': [u'application/json', u'application/xml', u'text/html', u'*/*' ],
            u'input_types': [u'application/json', u'application/x-www-form-urlencoded'],
            u'params': {
                u'count': {
                    u'desc': u'Number of results',
                    u'type': u'number',
                    u'required': False,
                    u'default': 20
                },
                u'filter': {
                    u'desc': u"If set, only 'important' fields are returned",
                    u'type': u'boolean',
                    u'required': False,
                    u'default': True
                }
            },
            u'uri': u'/code/TwitterComponent/home_timeline'
        },
        u'timeline': {
            u'desc': u'You can GET the timeline of the user.',
            u'output_types': [u'application/json', u'application/xml', u'text/html', u'*/*' ],
            u'input_types': [u'application/json', u'application/x-www-form-urlencoded'],
            u'params': {
                u'count': {
                    u'desc': u'Number of results',
                    u'type': u'number',
                    u'required': False,
                    u'default': 20
                },
                u'filter': {
                    u'desc': u"If set, only 'important' fields are returned",
                    u'type': u'boolean',
                    u'required': False,
                    u'default': True
                }
            },
            u'uri': u'/code/TwitterComponent/timeline'
        }
    }

    _dict_compare(cdef['services']['status'], services_def['status'])
    _dict_compare(cdef['services']['home_timeline'], services_def['home_timeline'])
    _dict_compare(cdef['services']['timeline'], services_def['timeline'])


def test_45_twitter_doc():
    """
    Test that we can retrieve a document at the doc URI of a component.

    """
    cdef, resp = _get_data("/code/TwitterComponent")
    doc_uri    = cdef['doc']
    doc, resp  = _get_data(doc_uri)
    assert(type(doc) in [ string, unicode ])
    assert("Twitter" in doc)
    

def test_50_make_resource():
    """
    Test creation of a new resource.

    """
    cdef, resp = _get_data("/code/TwitterComponent")

    d = {
            "foo"                   : { "blah" : 123 },
        }
    data, resp = _send_data(DOCROOT + "/code/TwitterComponent", d)
    assert(resp.getStatus() == 400)
    assert("Malformed resource parameter definition. Unknown key: foo" in data)

    d = {
            "params"                   : { "account_password" : "Foo", "account_name" : "Bar" },
        }
    data, resp = _send_data(DOCROOT + "/code/TwitterComponent", d)
    assert(resp.getStatus() == 400)
    assert("Missing mandatory parameter 'suggested_name' in section 'resource_creation_params'" in data)

    d = {
            "params"                   : { "account_password" : "Foo" },
        }
    data, resp = _send_data(DOCROOT + "/code/TwitterComponent", d)
    assert(resp.getStatus() == 400)
    assert("Missing mandatory parameter 'account_name' in section 'params'" in data)

    d = {
            "params"                   : { "account_password" : 123 },
        }
    data, resp = _send_data(DOCROOT + "/code/TwitterComponent", d)
    assert(resp.getStatus() == 400)
    assert("Incompatible type for parameter 'account_password' in section 'params'" in data)

    """
    d = {
            "params"                   : { "account_password" : "Foo", "account_name" : "Bar", "blah" : 123 },
        }
    data, resp = _send_data(DOCROOT + "/code/TwitterComponent", d)
    assert(resp.getStatus() == 400)
    assert("Unknown parameter in 'params' section: blah" in data)

    d = {
            "params"                   : { "account_password" : "Foo", "account_name" : "Bar" },
            "resource_creation_params" : { "suggested_name" : "foobar", "blah" : 123 }
        }
    data, resp = _send_data(DOCROOT + "/code/TwitterComponent", d)
    print "@@@@@@@@@@@@@@ data: ", data
    assert("Unknown parameter in 'resource_creation_params' section: blah" in data)
    assert(resp.getStatus() == 400)
    """

    d = {
            "params"                   : { "account_password" : "Foo", "account_name" : "Bar" },
            "resource_creation_params" : { "suggested_name" : "_test_foobar", "desc" : "A foobar resource" }
        }
    TEST_RESOURCES.append("/resource/_test_foobar")
    data, resp = _send_data(DOCROOT + "/code/TwitterComponent", d)
    assert(resp.getStatus() == 201)
    assert(data['status']   == "created")
    assert(data['name']     == "_test_foobar")
    assert(data['uri']      == DOCROOT + "/resource/_test_foobar")
    assert(len(data)        == 3)

def test_55_examine_resource():
    """
    Test retrieval of information about a reosurce.

    """
    data, resp = _get_data("/resource/_test_foobar")
    assert(resp.getStatus() == 200)

    resource_def = {
        "services": {
            "status": {
                "uri": DOCROOT + "/resource/_test_foobar/status", 
                "desc": "You can GET the status or POST a new status to it.",
                'output_types': [u'application/json', u'application/xml', u'text/html', u'*/*' ],
                u'input_types': [u'application/json', u'application/x-www-form-urlencoded'],
            }, 
            "timeline": {
                "uri": DOCROOT + "/resource/_test_foobar/timeline", 
                "desc": "You can GET the timeline of the user.",
                'output_types': [u'application/json', u'application/xml', u'text/html', u'*/*' ],
                u'input_types': [u'application/json', u'application/x-www-form-urlencoded'],
                'params': {
                    'count': {
                        'desc': 'Number of results',
                        'type': 'number',
                        'required': False,
                        'default': 20
                    },
                    'filter': {
                        'desc': "If set, only 'important' fields are returned",
                        'type': 'boolean',
                        'required': False,
                        'default': True
                    }
                },
             },
            'home_timeline': {
                "uri": DOCROOT + "/resource/_test_foobar/home_timeline", 
                'desc': 'You can GET the home timeline of the user.',
                'output_types': [u'application/json', u'application/xml', u'text/html', u'*/*' ],
                u'input_types': [u'application/json', u'application/x-www-form-urlencoded'],
                'params': {
                    'count': {
                        'desc': 'Number of results',
                        'type': 'number',
                        'required': False,
                        'default': 20
                    },
                    'filter': {
                        'desc': "If set, only 'important' fields are returned",
                        'type': 'boolean',
                        'required': False,
                        'default': True
                    }
                },
            },
        }, 
        "uri": DOCROOT + "/resource/_test_foobar", 
        "name": "_test_foobar", 
        "desc": "A foobar resource"
    }
    _dict_compare(data, resource_def)


def test_60_make_partial_resource():
    """
    Test creation of a new resource.

    """
    cdef, resp = _get_data("/code/TwitterComponent")

    d = {
            "params"                   : { "account_password" : "FOOOOOOOOOOOOOOOOOO" },
            "resource_creation_params" : { "suggested_name" : "_test_partial_base", "desc" : "A partial test resource", "specialized" : False }
        }
    TEST_RESOURCES.append("/specialized/_test_partial_base")
    data, resp = _send_data(DOCROOT + "/code/TwitterComponent", d)
    assert(resp.getStatus() == 400)
    assert("Missing mandatory parameter 'account_name' in section 'params'" in data)

    d['resource_creation_params']['specialized'] = True
    data, resp = _send_data(DOCROOT + "/code/TwitterComponent", d)

    assert(resp.getStatus() == 201)
    assert(data['status']   == "created")
    assert(data['name']     == "_test_partial_base")
    assert(data['uri']      == DOCROOT + "/specialized/_test_partial_base")
    assert(len(data)        == 3)

def test_62_examine_partial_resource():
    """
    Test retrieval of information about a partial reosurce.

    """
    data, resp = _get_data("/specialized/_test_partial_base")
    assert(resp.getStatus() == 200)

    resource_def = {
        "resource_creation_params": {
            "suggested_name": {
                "desc": "Can be used to suggest the resource name to the server", 
                "type": "string", 
                "required": True, 
            }, 
            "desc": {
                "desc": "Specifies a description for this new resource", 
                "type": "string", 
                "required": False, 
                "default": "A partial test resource"
            }
        }, 
        "doc": "/specialized/_test_partial_base/doc", 
        "services": {
            "status": {
                "desc": "You can GET the status or POST a new status to it.", 
                'output_types': [u'application/json', u'application/xml', u'text/html', u'*/*' ],
                'input_types': [u'application/json', u'application/x-www-form-urlencoded'],
                "uri": "/code/TwitterComponent/status"
            }, 
            "home_timeline": {
                "desc": "You can GET the home timeline of the user.", 
                'output_types': [u'application/json', u'application/xml', u'text/html', u'*/*' ],
                'input_types': [u'application/json', u'application/x-www-form-urlencoded'],
                "params": {
                    "count": {
                        "desc": "Number of results", 
                        "type": "number", 
                        "required": False, 
                        "default": 20
                    }, 
                    "filter": {
                        "desc": "If set, only 'important' fields are returned", 
                        "type": "boolean", 
                        "required": False, 
                        "default": True
                    }
                }, 
                "uri": "/code/TwitterComponent/home_timeline"
            }, 
            "timeline": {
                "desc": "You can GET the timeline of the user.", 
                'output_types': [u'application/json', u'application/xml', u'text/html', u'*/*' ],
                'input_types': [u'application/json', u'application/x-www-form-urlencoded'],
                "params": {
                    "count": {
                        "desc": "Number of results", 
                        "type": "number", 
                        "required": False, 
                        "default": 20
                    }, 
                    "filter": {
                        "desc": "If set, only 'important' fields are returned", 
                        "type": "boolean", 
                        "required": False, 
                        "default": True
                    }
                }, 
                "uri": "/code/TwitterComponent/timeline"
            }
        }, 
        "desc": "A partial test resource", 
        "params": {
            "account_password": {
                "is_settable": False, 
                "desc": "Password", 
                "type": "password", 
                "required": True, 
                "default": "*** PROVIDED BY COMPONENT SPECIALIZATION ***"
            }, 
            "account_name": {
                "desc": "Twitter account name", 
                "type": "string", 
                "required": True, 
            }
        }, 
        "uri": "/specialized/_test_partial_base", 
        "name": "_test_partial_base"
    }

    _dict_compare(data, resource_def)


def test_65_make_from_partial_resource():
    """
    Test creation of a new resource, based on partial resource.

    """
    uri = "/specialized/_test_partial_base"
    cdef, resp = _get_data(uri)

    d = {
            "foo"                   : { "blah" : 123 },
        }
    data, resp = _send_data(DOCROOT + uri, d)
    assert(resp.getStatus() == 400)
    assert("Malformed resource parameter definition. Unknown key: foo" in data)

    d = {
            "params"                   : { "account_password" : "Foo", "account_name" : "Bar" },
        }
    data, resp = _send_data(DOCROOT + uri, d)
    assert(resp.getStatus() == 400)
    assert("Missing mandatory parameter 'suggested_name' in section 'resource_creation_params'" in data)

    d = {
            "params"                   : { "account_password" : "Foo" },
        }
    data, resp = _send_data(DOCROOT + uri, d)
    assert(resp.getStatus() == 400)
    assert("Missing mandatory parameter 'account_name' in section 'params'" in data)

    """
    d = {
            "params"                   : { "blah" : 123 },
        }
    data, resp = _send_data(DOCROOT + uri, d)
    assert(resp.getStatus() == 400)
    assert("Unknown parameter in 'params' section: blah" in data)

    d = {
            "params"                   : { "account_password" : "Foo", "account_name" : "Bar" },
            "resource_creation_params" : { "suggested_name" : "foobar", "blah" : 123 }
        }
    data, resp = _send_data(DOCROOT + uri, d)
    assert("Unknown parameter in 'resource_creation_params' section: blah" in data)
    assert(resp.getStatus() == 400)
    """

    d = {
            "params"                   : { "account_password" : "Foo", "account_name" : "Bar" },
            "resource_creation_params" : { "suggested_name" : "_test_foobar_from_partial" }  #    , "desc" : "A foobar resource" }
        }
    TEST_RESOURCES.append("/resource/_test_foobar_from_partial")
    data, resp = _send_data(DOCROOT + uri, d)
    assert(resp.getStatus() == 201)
    assert(data['status']   == "created")
    assert(data['name']     == "_test_foobar_from_partial")
    assert(data['uri']      == DOCROOT + "/resource/_test_foobar_from_partial")
    assert(len(data)        == 3)

 
def test_70_positional_params():
    """
    Test that positional parameters can be used successfully.

    """
    # Start by creating a file storage resource
    d = {
            "resource_creation_params" : { "suggested_name" : "_test_foobarstorage", "desc" : "A foobar storage resource" }
        }
    TEST_RESOURCES.append("/resource/_test_foobarstorage")
    data, resp = _send_data(DOCROOT + "/code/StorageComponent", d)
    assert(resp.getStatus() == 201)
    assert(data['status']   == "created")
    assert(data['name']     == "_test_foobarstorage")
    assert(data['uri']      == DOCROOT + "/resource/_test_foobarstorage")
    assert(len(data)        == 3)

    # Delete anything that's there
    cdef, resp = _get_data("/resource/_test_foobarstorage/files")
    assert(resp.getStatus() == 200)
    assert(cdef == [])

    # Store a file
    data, resp = _send_data(DOCROOT + "/resource/_test_foobarstorage/files/foo", "This is a buffer")
    assert(data == "Successfully stored")
    assert(resp.getStatus() == 200)

    # Retrieve a file
    cdef, resp = _get_data("/resource/_test_foobarstorage/files/foo")
    assert(cdef == 'This is a buffer')
    assert(resp.getStatus() == 200)

    # Delete the file again
    buf, resp = _delete(DOCROOT + "/resource/_test_foobarstorage/files/foo")
    assert(resp.getStatus() == 200)

def test_80_japanese_message():
    """
    Test Japanese message.

    """
    d = {
            "params"                   : { "api_key" : "this_is_an_api_key" },
            "resource_creation_params" : { "suggested_name" : "_test_component", "desc" : "A foobar storage resource" }
        }
    TEST_RESOURCES.append("/resource/_test_component")
    data, resp = _send_data(DOCROOT + "/code/TestComponent", d)
    assert(resp.getStatus() == 201)
    assert(data['status']   == "created")
    assert(data['name']     == "_test_component")
    assert(data['uri']      == DOCROOT + "/resource/_test_component")
    assert(len(data)        == 3)

    data, resp = _get_data(DOCROOT + "/resource/_test_component/japanese");
    # This is a Japanese message (kore wa nihongo no message desu).
    # See TestComponent.japanese().
    expected = u'\u3053\u308c\u306f\u65e5\u672c\u8a9e\u306e\u30e1\u30c3\u30bb\u30fc\u30b8\u3067\u3059\u3002'
    #print(repr(data))
    #print(repr(expected))
    assert(data == expected)
    assert(resp.getStatus() == 200)

def test_90_choice_params():
    """
    Testing resource creation for components with choices for their parameters.

    """
    d = {
            "params"                   : { "api_key" : "this_is_an_api_key", "foo_1" : "xyz" },
            "resource_creation_params" : { "suggested_name" : "_test_component_2", "desc" : "A foobar storage resource" }
        }
    TEST_RESOURCES.append("/resource/_test_component_2")
    data, resp = _send_data(DOCROOT + "/code/TestComponent", d)
    assert(resp.getStatus() == 400)
    assert(data == "Value 'xyz' for parameter 'foo_1' is not one of the permissible choices.")

    d['params']['foo_1'] = "Foo B"
    d['params']['foo_2'] = 19
    data, resp = _send_data(DOCROOT + "/code/TestComponent", d)
    assert(resp.getStatus() == 400)
    assert(data == "Value '19' for parameter 'foo_2' is not one of the permissible choices.")

    d['params']['foo_2'] = 2
    data, resp = _send_data(DOCROOT + "/code/TestComponent", d)
    assert(resp.getStatus() == 201)

def test_95_multi_choice_params():
    """
    Testing resource creation for components with multiple choices for their parameters.

    """
    d = {
            "params"                   : { "another_parameter" : [ 3, 123.4 ], "third_parameter" : [ 'A', 'B' ] }, 
            "resource_creation_params" : { "suggested_name" : "_test_component_3", "desc" : "A foobar test resource" }
        }
    TEST_RESOURCES.append("/resource/_test_component_3")
    data, resp = _send_data(DOCROOT + "/code/PythonTestComponent", d)
    assert(resp.getStatus() == 400)
    assert(data == "List value '3' for parameter 'another_parameter' is not one of the permissible choices.")

    d['params']['another_parameter'] =  "3"
    data, resp = _send_data(DOCROOT + "/code/PythonTestComponent", d)
    assert(resp.getStatus() == 400)
    assert(data == "Value '3' for parameter 'another_parameter' is not one of the permissible choices.")

    d['params']['another_parameter'] =  2
    data, resp = _send_data(DOCROOT + "/code/PythonTestComponent", d)
    assert(resp.getStatus() == 201)

    d['params']['another_parameter'] =  "2"
    data, resp = _send_data(DOCROOT + "/code/PythonTestComponent", d)
    assert(resp.getStatus() == 201)

    d['params']['another_parameter'] =  [ 1, 2 ]
    data, resp = _send_data(DOCROOT + "/code/PythonTestComponent", d)
    assert(resp.getStatus() == 201)

def test_999_cleanup():
    """
    Find all resources starting with "_test_" and delete them.

    This is actually more of a cleanup function.

    """
    """
    rlist, resp = _get_data('/resource')
    assert(resp.getStatus() == 200)
    # Find any old test resources and delete them.
    for name in rlist:
    """
    global TEST_RESOURCES
    for name in TEST_RESOURCES:
        if "/_test_" in name:
            buf, resp = _delete(DOCROOT + name)
    TEST_RESOURCES = []




#
# Some utility methods
#
def _log(msg, eol=True, cur_time=None, continuation=False):
    """
    Log a message.

    @param msg:          The message to be logged.
    @type  msg:          string

    @param eol:          Flag indicating whether we put an '\n' at the end.
    @type  eol:          boolean

    @param continuation: Flag indicating whether this continues a previous line (don't print time stamp).
    @type  continuation: boolean

    """
    buf = ""
    if not continuation:
        if not cur_time:
            start_time = datetime.datetime.now()
        else:
            start_time = cur_time
        buf = "### %s - " % start_time.isoformat()
    buf += msg
    if eol:
        buf += "\n"
    print buf,


def _make_timediff_str(start_time, end_time):
    """
    Return properly formatted string with difference in start and end time (datetime.datetime object).

    """
    td = end_time - start_time
    return "%d.%06d" % (td.seconds, (td.microseconds * 1000000) / 1000000)


def run_all_tests(methods):
    print "--- Starting all test..."
    overall_start_time = datetime.datetime.now()
    for method, method_name in methods:
        start_time = datetime.datetime.now()
        _log("Executing: %s" % string.ljust(method_name, 36), cur_time=start_time, eol=False)
        method()
        msg = "Ok"
        end_time = datetime.datetime.now()
        _log(" - Duration: %ss - %s" % (_make_timediff_str(start_time, end_time), msg), continuation=True)
    overall_end_time = datetime.datetime.now()
    print "--- Completed run. Duration: %s\n" % (_make_timediff_str(overall_start_time, overall_end_time))



if __name__ == '__main__':
    #
    # Collect the names of all test methods
    #

    params = sys.argv[1:]

    test_methods = [ name for name in dir() if name.startswith("test_") ]
    test_methods.sort()
    methods = [ (globals()[method_name], method_name) for method_name in test_methods ]

    if "loop" in params:
        while (True):
            run_all_tests(methods)
    else:
        run_all_tests(methods)

