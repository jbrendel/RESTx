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
Input/sOutputs JSON representation of data, dealing with some Ext JS specific issues.
 
"""

# Python imports
import restxjson as json

# RESTx imports
from restx.render.jsonrenderer import JsonRenderer


class ExtJsonRenderer(JsonRenderer):
    """
    Class to render data as JSON in an Ext JS specific manner.
        
    """
    CONTENT_TYPE = "application/ext+json; charset=UTF-8"

    def parse(self, data):
        """
        Take input in this renderer's format and produce an object.
        
        @param data:        An input containing the serialized representation of an
                            object in this renderer's format.
        @param data:        string
        
        @return:            Object that was de-serialized from this input.
        @rtype:             object
        
        """
        obj = json.loads(data)
        return obj['undefined']
 
