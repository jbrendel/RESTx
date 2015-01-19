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

from restx.render.baserenderer import BaseRenderer

class TextRenderer(BaseRenderer):
    """
    A text renderer
    
    """

    CONTENT_TYPE = "text/plain; charset=UTF-8"

    def render(self, data, top_level=False):
        """
        Render the provided data for output.
        
        @param data:        An object containing the data to be rendered.
        @param data:        object
        
        @param top_level:   Flag indicating whether this we are at the
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
        return str(data)

    def parse(self, data):
        """
        Take input in this renderer's format and produce an object.
        
        @param data:        An input containing the serialized representation of an
                            object in this renderer's format.
        @param data:        string
        
        @return:            Object that was de-serialized from this input.
        @rtype:             object
        
        """    
        return data
