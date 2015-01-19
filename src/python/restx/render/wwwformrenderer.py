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
Parses application/x-www-form-urlencoded data. No output.
 
"""

# Python imports
import restxjson as json
import urllib

# RESTx imports
from restx.render.baserenderer import BaseRenderer


class WwwFormRenderer(BaseRenderer):
    """
    Class to render/parse data from the www-form encoding.
        
    """
    CONTENT_TYPE = "application/x-www-form-urlencoded; charset=UTF-8"
    CAN_RENDER   = False

    def parse(self, data):
        """
        Assuming the input is in application/x-www-form-urlencoded format, return values as dict.

        @param data:   An input string, containing the entire form data.
        @type data:    string

        @return:       Dictionary with the decoded values
        @rtype:        dict

        """
        name_val_pairs = data.split("&")
        d = dict()
        for nvpair in name_val_pairs:
            elems = nvpair.split("=")
            if len(elems) == 1:
                # No value? That's as if the value wasn't set at all
                continue
            name, value = elems
            name  = name.strip()
            value = urllib.unquote_plus(value.strip())
            # A name may appear more than once (multi-choice select box). In that case,
            # we should create a list
            if name in d:
                if type(d[name]) is list:
                    d[name].append(value)
                else:
                    d[name] = [ d[name], value ]
            else:
                d[name] = value
        return d

