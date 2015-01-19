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

#
# The CSV renderer will only work if it gets a list of dictionaries
# or a list of lists.
#
# In case of a list of dictionaries, the keys in the first dictionary
# determine the columns that are exported.
#
# In case of a list of lists, the number of elements in the first sub-
# list determines the number of overall columns. The column names will
# in that case simply be "column_1", "column_2", etc.
#
# Any first-level list elements that are not of the required format
# will be ignored.
# 
# The values for individual cells need to be simple. Any complex or
# compouned elements are ignored.
#

class CsvRenderer(BaseRenderer):
    """
    A very simple CSV renderer
    
    """

    CONTENT_TYPE = "text/csv"
    CAN_PARSE    = False

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
        if type(data) not in [ list, tuple ]:
            raise RestxException("CsvRenderer: Data type '%s' not suitable for CSV renderer." % str(type(data)))

        #
        # Determine the type of data we have here, list of lists or list of dicts.
        # Determine the column names accordingly.
        #
        first_row = data[0]
        if type(first_row) is dict:
            keys = first_row.keys()
            keys.sort()
            list_type = False
        elif type(first_row) in [ list, tuple ]:
            keys = [ "column_%d" % (i+1) for i,d in enumerate(first_row) ]
            list_type = True
        else:
            raise RestxException("CsvRenderer: First row is neither dict nor list, but '%s'." % str(type(first_row)))

        out = ';'.join(keys) + "\n"

        for row in data:
            try:
                if list_type:
                    out += ';'.join([ str(c) for c in row ]) + "\n"
                else:
                    out += ';'.join([ str(row.get(cname, "")) for cname in keys ]) + "\n"
            except:
                # Silently ignore any issues
                pass

        return out

