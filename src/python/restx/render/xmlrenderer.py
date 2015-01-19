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

from copy import copy

from restx.render.baserenderer import BaseRenderer
from org.mulesoft.restx.util   import Url
from restx.core.util           import bool_view


class XmlRenderer(BaseRenderer):
    """
    A very simple XML renderer
    
    """

    CONTENT_TYPE = "application/xml; charset=UTF-8"
    CAN_PARSE    = False

    __indent_spaces = "    "

    def __init__(self, renderer_args=None):
        super(XmlRenderer, self).__init__(renderer_args)
        self.__indent_level = 0

    def __dict_render(self, data):
        """
        Take Python dictionary and produce XML output.
        
        The output of a dictionary is modified by some of the renderer arguments.
        
        @param data:    A dictionary that needs to be rendered in XML.
        @type  data:    dict
        
        @return:        XML representation of the dictionary.
        @rtype:         string        
        """
        keys = copy(data.keys())
        # In the future we might want to display particular items
        # in specific positions, but for now, we just sort the
        # items alphabetically.
        keys.sort()
        out = ""
        indent = self.__indent_level * self.__indent_spaces
        for key in keys:
            key_str = str(key).replace(" ", "_")
            out += indent + "<%s>\n" % key_str
            out += self.render(data[key])
            out += indent + "</%s>\n" % key_str
        return out


    def __list_render(self, data):
        """
        Take Python list and produce XML output.
        
        The output of a list is modified by some of the renderer arguments.
        
        @param data:    A list that needs to be rendered in HTML.
        @type  data:    list
        
        @return:        XML representation of the list.
        @rtype:         string
        
        """
        indent = self.__indent_level * self.__indent_spaces
        out = indent + "<rxlist>\n"
        self.__indent_level += 1
        indent_plus = self.__indent_level * self.__indent_spaces
        for i, elem in enumerate(data):
            out += "%s<rxitem>\n%s%s</rxitem>\n" % (indent_plus, self.render(elem), indent_plus)
        out += indent + "</rxlist>\n"
        self.__indent_level -= 1
        return out


    def __plain_render(self, data):
        """
        Take a non-list, non-dict Python object and produce XML.
        
        A simple conversion to string is performed.
        
        @param data:    A Python object
        @type  data:    object
        
        @return:        XML representation of the object.
        @rtype:         string

        """
        if type(data) is str  or  type(data) is unicode:
            if data.startswith("http://") or data.startswith("https://")  or data.startswith("/"):
                data = Url(data)
        if data is None:
            out = "---"
        elif type(data) is Url:
            out = str(data)
        elif type(data) is bool:
            out = bool_view(data)
        else:
            if type(data) is not unicode:
                data_str = str(data)
            else:
                data_str = data
            out = data_str
        if not out.endswith("\n"):
            out += "\n"
        return self.__indent_level * self.__indent_spaces + out


    def render(self, data, top_level=False):
        """
        Render the provided data for output.
        
        @param data:        An object containing the data to be rendered.
        @param data:        object
        
        @param top_level:   Flag indicating whether we are at the
                            top level for output (this function is called
                            recursively and therefore may not always find
                            itself at the top level). This is important for
                            some renderers, since they can insert any framing
                            elements that might be required at the top level.
                            However, for the JSON renderer this is just
                            ignored.
        @param top_level:   boolean
        
        @return:            Output buffer with completed representation.
        @rtype:             string
        
        """
        self.__indent_level += 1
        if top_level:
            out = '<?xml version="1.0" encoding="UTF-8" ?>\n<rxdoc>\n'
        else:
            out = ""
        if type(data) is dict:
            out += self.__dict_render(data)
        elif type(data) in [ list, tuple ]:
            out += self.__list_render(data)
        else:
            out += self.__plain_render(data)
        if top_level:
            out += "</rxdoc>\n"
        else:
            self.__indent_level -= 1
        return out

