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
The Filter component takes input from a single resource, assuming
the input is formatted as a list of dictionaries, or a dictionary
of dictionaries. It detects the format automatically.

Based on a filter expression, it removes top-level elements from
the input.

"""

import shlex

# Imports all aspects of the API
from restx.components.api import *

class Filter(BaseComponent):

    # Name, description and doc string of the component as it should appear to the user.
    NAME             = "Filter"
    DESCRIPTION      = "Capable of filtering input based on certain filter criteria."
    DOCUMENTATION    = """<pre>
The RESTx Filter component
==========================
This component allows the creation of filtering resources. Input from another
resource or an external URI is taken and filtered based on a specified query.


The resource or URI is expected to produce input consisting of dictionaries or
lists. Each element in those dictionaries or lists is allowed to be a dictionary
or list itself.


Elements are filtered based on 'Filter Expressions'. A filter expression consists
of a 'Search Expression' (which identifies an element in a complex data structure)
and a 'Value Expression' (which identifies the value(s) that this element must
match).


Currently, only simple filter expressions are supported.  AND, OR, XOR or
parenthesis to build more complex filter expressions might be provided later.


Filter expressions are used to define a PASS filter: Only those elements matching
this pass filter appear in the output.


Quick start
-----------
    Example 1:


        Assume this input:


            [
                [ "foo", "bar", "blah" ],
                [ "test", "123", "xyz" ]
            ]


        Apply this filter expression:


            1 = bar


        This means that array element with index 1 is compared to 'bar'. Therefore, the
        output of this is going to be:


            [
                [ "foo", "bar", "blah" ],
            ]


    Example 2:


        Input:


            [
                { "foo" : "xyz", "bar" : 123 },
                { "foo" : "abc", "bar" : 456 }
            ]


        Filter:


            bar = 456


        Output:

            [
                { "foo" : "abc", "bar" : 456 }
            ]


    Example 3:


        Input:

            
            [
                { "foo" : "xyz", "bar" : [ 'x', 'y', { 'elem1' : 'Test' } ] },
                { "foo" : "abc", "bar" : [ 'q', 'q', { 'elem1' : 'Other' } ] }
            ]


        Filter:


            bar/2/elem1 = Other


        Output:


            [
                { "foo" : "abc", "bar" : [ 'q', 'q', { 'elem1' : 'Other' } ] }
            ]


Search Expressions
------------------
Search expressions are used to identify a particular element of the input. This
is much a much simpler mechanism than XPath. A full XPath compatible filter
component might be built in the future.


Different components of the search expression are separated by '/'. If a component
in the search expression contains a '/', ' ' or one of the characters that are
used in operators ('!', '<', '>', '=') then that element needs to be quoted using
double quotes. For example:


    foo/"First Name"/bar


Search expressions are processed from left to right to traverse down into a
top-level element. If traversal isn't possible because the data structure of
the element doesn't match the filter expression (a dictionary key is defined
when the element is actually a list, for example) then the element is considered
as not-matched.


For example, assume the input is a list of dictionaries (top level elements),
as follows:


        [
            { "foo" : 123,
              "bar" : [ "x", "y", "z", { "sub_a" : "Test",
                                         "sub_b" : [ 11, 22, 33 ]
                                       }
                      ]
            },
            { "foo" : 456,
              "bar" : [ "a", "b", "c", { "sub_a" : "Other text",
                                         "sub_b" : [ 100, 200, 300 ]
                                       }
                      ]
            }
        ]


Now assume a filter expression as follows:


    bar/3/sub_b/1
     |  |   |   |_____ match array element with index 1 or dictionary with numeric key 1
     |  |   |_________ find dictionary key 'sub_b'
     |  |_____________ find array element with index 3 or dictionary with numeric key 3
     |________________ find dictionary key 'bar' (contains an array)


So for our first array element (index 0) in our sample input, this filter
expression gets us the number 22, while for our second element it gets us
the number 200.


Note that the very same filter expression is still valid if the input arrives
as a dictionary:


    {
        "elem1" : { "foo" : 123,
                    "bar" : [ .......
        "elem2" : { "foo" : 456,
                    "bar" : [ .......
    }


That is because the filter expression is only applied to the
top level elements, not the top-level identifier (array index or key in input
dictionary):


Numeric elements in the search expression are cast to numbers. This makes them
suitable to address array indices as well as dictionary elements with numeric
key. If you want to keep them as string, please specify them in quotes. For
example:


    a/"3"/b


That way, '3' will be kept as a string, only suitable to be used as key into
a dictionary, not as index into an array.


Value expressions
-----------------
A value expression determines the values that an element (identified by a 
search expression) has to have to be considered as 'matched'.


Value expressions start with one of these operators:


    =
    !=
    <
    >
    <=
    >=


A complete value expression looks like this:


    <op> <value>


For example:


    = foo         # compares element to string 'foo'
    > 123         # compares element to number 123
    > "123"       # compares element to string '123'
    = true        # compares element to boolean TRUE
    = "true"      # compares element to string 'true'


Note that the data type for the comparison is implied by the specified value.
If it looks like a number and is not in quotes then it is assumed to be a number.
If the identified input element is not of the necessary type or cannot be cast
to that type then the element is considered not-matched.
</pre>
"""

    # Resource creation time parameters.
    # Each parameter is created through a ParameterDef object, which encapsulates
    # the definition of the parameter. The PARAM_* argument determines the type
    # of the parameter. Currently, we know PARAM_STRING, PARAM_NUMBER and PARAM_BOOL.
    PARAM_DEFINITION = {
                           "input_resource_uri"   : ParameterDef(PARAM_STRING, "URI of a resource", required=True),
                           "filter_expression_1"  : ParameterDef(PARAM_STRING, "Filter expression", required=True),
                           "filter_expression_2"  : ParameterDef(PARAM_STRING, "Filter expression", required=False, default=""),
                           "filter_expression_3"  : ParameterDef(PARAM_STRING, "Filter expression", required=False, default=""),
                           "match_all"            : ParameterDef(PARAM_BOOL,   "If set, all filiter expressions need to match, othrwise, a single match is sufficient",
                                                                 required=False, default=True)
                       }
    
    # A dictionary with information about each exposed service method (sub-resource).
    SERVICES         = {
                           "filter" : {
                               "desc" : "Get the filtered result",
                               "params" : {
                                   "negate" : ParameterDef(PARAM_BOOL, "Reverse the filter expression", required=False, default=False)
                                }
                           }
                       }

    __OP_LIST = {
        "="  : lambda x,y: x == y,
        ">"  : lambda x,y: x > y,
        ">=" : lambda x,y: x >= y,
        "<"  : lambda x,y: x < y,
        "<=" : lambda x,y: x <= y,
        "!=" : lambda x,y: x != y,
    }

    def __parse_value(self, value):
        #
        # Examine the value, extracted as a string from a filter
        # expression. Convert to boolean or numeric type if possible.
        #
        if value in [ "true", "false" ]:
            if value == "true":
                value = True
            else:
                value = False
        else:
            # See if the value can be converted to a number
            try:
                value = int(value)
            except:
                try:
                    value = float(value)
                except:
                    # Still not? Just leave as string then
                    pass
        return value


    def _filter_compile(self, filter_expression):
        #
        # A filter expression may look like this:
        #
        #     "first name"/1/2/blah/foo/"some / test" = 123
        #
        # We want to return the following tuple:
        #
        #     (
        #         [ 'first name', 1, 2, 'blah', 'foo', 'some / test' ],
        #         '=',
        #         123
        #     )
        #
        # If the filter expression cannot be parsed properly, we
        # return None.
        #
        elems = shlex.split(filter_expression)
        # The last element must be the value
        value = elems[-1]
        # Where did the value start?
        vi = filter_expression.rfind(value)
        if filter_expression[vi-1] != '"':
            value = self.__parse_value(value)

        # Second to last element must be the operator
        op = elems[-2]

        # All the text before the operator must be the
        # actual search expression.
        oi = filter_expression.rfind(op, 0, vi-1)
        se = filter_expression[:(oi-1)]

        # At this point, se can look like this: '"  first  name  "/1/2/blah/foo/" some / test "'
        elems = list()
        while se:
            if se.startswith("/"):
                se = se[1:]
            qi = se.find('"')
            if qi > 0:
                # We have some text before the first quote. Might have to be split
                # along the '/' markers.
                prefix = se[:qi]
                if not prefix.endswith("/"):
                    raise RestxException("Malformed search expressions: Expecting '/' before '\"'")
                elems.extend([ self.__parse_value(e) for e in prefix.split("/")[:-1] ])   # Skip last element (empty), which is caused by traling '/'
                se = se[qi:]
            elif qi == 0:
                # This starts with a '"'. So we get the starting text
                nqi = se.find('"', qi+1)
                if nqi == -1:
                    raise RestxException("Malformed search expressions: Missing closing quotes")
                elems.append(se[qi+1:nqi])
                se = se[nqi+1:]          # Get the postfix
                if se and not se.startswith("/"):
                    raise RestxException("Malformed search expressions: Expecting '/' after '\"'")
            else:
                # No quotes in the remaining string
                elems.extend([ self.__parse_value(e) for e in se.split("/") ])   # Skip last element (empty), which is caused by traling '/'
                break

        return ( elems, op, value )


    def _get_elem(self, obj, search_list):
        #
        # Traverse down into a complex object
        # based on the search list.
        # Just throw if the structure of the object
        # doesn't match the search list.
        #
        for elem in search_list:
            obj = obj[elem]
        return obj
        
    def filter(self, method, input, negate):
        #
        # Parse the filter expression, performing some sanity checking
        #
        search_expres = list()   # List of tuples of all search lists, operators and values
        res = self._filter_compile(self.filter_expression_1)
        if not res:
            raise RestxException("Filter epxression 1 is invalid")
        search_expres.append(res)

        if self.filter_expression_2:
            res = self._filter_compile(self.filter_expression_2)
            if not res:
                raise RestxException("Filter epxression 2 is invalid")
            search_expres.append(res)

        if self.filter_expression_3:
            res = self._filter_compile(self.filter_expression_3)
            if not res:
                raise RestxException("Filter epxression 3 is invalid")
            search_expres.append(res)

        status, data = self.accessResource(self.input_resource_uri)
        if status != 200:
            raise RestxException("Could not get data from input resource")

        if type(data) is dict:
            is_dict = True
            keys    = data.keys()
            out     = dict()
            def adder(k,v):
                out[k] = v
        else:
            is_dict = False
            keys    = range(len(data))
            out     = list()
            def adder(k,v):
                out.append(v)
            
        for k in keys:
            top_level_elem = data[k]
            matched_count  = 0
            matched        = False
            try:
                # Match against all of any of the search expressions
                for (search_list, op, value) in search_expres:
                    elem = self._get_elem(top_level_elem, search_list)
                    if self.__OP_LIST[op](elem, value):
                        matched_count += 1
                        if not self.match_all  or  (matched_count == len(search_expres)):
                            matched = True
                            break
            except:
                pass
            if (matched and not negate)  or  (not matched and negate):
                adder(k, top_level_elem)

        return Result.ok(out)


