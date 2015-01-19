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
Base class for all content browser classes.

"""
# RESTx imports
import restx.settings as settings

from org.mulesoft.restx.exception     import RestxNotAcceptableException
from org.mulesoft.restx.component.api import HTTP, Result


class BaseBrowser(object):
    """
    A browser is a class that handles specific requests after they
    are assigned by the request-dispatcher.
    
    For example, there might be a specialized browser to deal with
    the installed components/code, another browser for server meta data
    and another to deal with resources.
    
    The RequestDispatcher instantiates specific browsers based on
    the URI prefix.
    
    This base class provides methods to detect the requested content
    type and to format output according to that content type.
    
    """
    '''
    def __accept_header_parsing(self, hdr_list):
        """
        Parses the accept header link and returns the most relevant header.

        The 'list' will only have more than one element if there were multiple
        'accept' header lines in the request. If you have a single accept header
        line with multiple, comma separated types, then it will still just be a
        single element in the list.

        The accumulated content types are sorted by their q parameter and are
        returned in a list, most-preferred type first.

        @param hdr_list:        List of values from accept header lines.
        @type hd_list:          list

        @return:                List of content types, sorted by prefrerence,
                                most preferred first.

        """
        # Create a list of all individual types that may be specified
        # in one or more header lines.
        elems = list()
        for hdr in hdr_list:
            elems.extend([ type_str.strip() for type_str in hdr.split(",") ])

        # Each element may have a q parameter, somewhere between 0 and 1. The
        # higher the value, the more desired that type is. If no q was defined
        # then the default is q=1. However, to make sure that those who have
        # no q defined appear first (that's usually the intend) we give them a
        # q=2 for sorting purposes.
        type_q_tuples = [ e.split(";") for e in elems ]

        # Below, the sorted() returns a list of iterable list elements, each eith
        # either one or two elements. We then only take the first element since
        # we are not interested in returning the q=* value.
        return [ e[0] for e in sorted(type_q_tuples, key=lambda x: x[1] if len(x) > 1 else "q=2", reverse=True) ]
    '''


    def __init__(self, request, renderer_args = None):
        """
        Initialize and perform analysis of request headers.
        
        The 'human_client' flag is set unless 'application/json'
        was requested in the accept header. This is because we
        are assuming that a non-human client wants the easily
        parsable json.
                        
        @param request:        This HTTP request.
        @type request:         RestxHttpRequest
        
        @param renderer_args:  A dictionary of arguments for the
                               chosen renderer. It's passed straight through
                               to the renderer and is not used by the browser.
        @type renderer_args:   dict (or None)
        
        """
        self.request        = request
        self.headers        = request.getRequestHeaders()
        self.header         = ""
        self.footer         = ""
        self.renderer_args  = renderer_args
        self.breadcrumbs    = list()
        self.context_header = list()  # Contextual menus or other header items, possibly displayed by renderer
    
    def renderOutput(self, data, renderer_class):
        """
        Take a Python object and return it rendered.
        
        This uses a specific renderer class to convert the raw
        data (a Python object) to data that can be sent back to
        the client.
        
        @param data:  A Python object that should consist only of dictionaries
                      and lists. The output is rendered in JSON, HTML, etc.
                      based on details we have gleaned from the request. For
                      example, there is a human_client flag, which if set indicates
                      that the output should be in HTML.
        @type data:   object

        @param renderer_class:  The class of the renderer, which was selected through content negotiation.
        @type renderer_class:   BaseRenderer
        
        @return:      Tuple with content type and rendered data, ready to be sent to the client.
        @rtype:       tuple of (string, string)

        """
        self.renderer_args.update(dict(breadcrumbs=self.breadcrumbs, context_header=self.context_header))
        renderer = renderer_class(self.renderer_args)
        return renderer.CONTENT_TYPE, renderer.base_renderer(data, top_level=True)
    
    def process(self):
        """
        Process the request.
        
        This needs to be overwritten with a specific implementation.
        
        @return:  Http return code and data as a tuple.
        @rtype:   tuple
        
        """
        return Result.ok("Base Browser")

                
