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
Allows users and clients to browse the server's installed code.

"""
# Java imports
import restxjson as json

# RESTx imports
import restx.settings as settings

from org.mulesoft.restx.exception       import RestxException
from org.mulesoft.restx.component.api   import Result

from restx.components                   import get_component_names, make_component

from restx.resources                    import makeResourceFromComponentObject, listResources, retrieveResourceFromStorage, getResourceUri,   \
                                               specializedOverwrite, deleteResourceFromStorage
from restx.core.basebrowser             import BaseBrowser
from restx.languages                    import *

from org.mulesoft.restx.util            import Url
from org.mulesoft.restx.component.api   import HTTP;

EXCLUDE_PREFIXES = [ "_" ]


def getComponentObjectFromPath(uri, resource_name = None):
    """
    Return the specified component class, based on a given URI.
    
    @param uri:             The official URI for this code.
    @type uri:              string

    @param resource_name:   Name of the resource for which the component was instantiated.
    @type resource_name:    string
    
    @return                 Class of the specified component
                            or None if no matching component class was found.
    @rtype                  A class derived from BaseComponent
    
    """
    path_elems     = uri[len(settings.PREFIX_CODE):].split("/")[1:]
    component_name = path_elems[0]   # This should be the name of the code element
    
    # Instantiate the component
    
    component = make_component(component_name)
    if component:
        # If this component needs to be instantiated for a resource
        # then we are also applying the resource information to it.
        component.setResourceName(resource_name)
    
    return component


class CodeBrowser(BaseBrowser):
    """
    Handles requests for code info.
    
    """
    def __init__(self, request):
        """
        Initialize the browser with the render-args we need for meta data browsing.
        
        @param request: Handle to the HTTP request that needs to be processed.
        @type request:  RestxHttpRequest
        
        """
        super(CodeBrowser, self).__init__(request,
                                          renderer_args = dict(no_annotations=True,
                                                               no_table_headers=False,
                                                               no_list_indices=False,
                                                               no_borders=False))
    
    def __process_get(self, is_code, prefix):
        """
        Respond to GET requests.
        
        When someone sends GET requests to the code then
        they want to browse the available code options.

        Same with spezialiced code.

        @param is_code:     Indicates whether this is a request for un-specialized code.
        @type is_code:      boolean

        @param prefix:      The prefix for this type of request.
        @type prefix:       string
        
        @return:  HTTP return structure.
        @rtype:   Result

        """
        # It's the responsibility of the browser class to provide breadcrumbs
        if is_code:
            dirname = "Code"
        else:
            dirname = "Specialized"
        self.breadcrumbs = [ ("Home", "/"), (dirname, prefix) ]

        if self.request.getRequestPath() == prefix:
            #
            # Just show the home page of the code browser (list of all installed (specialized) code)
            #
            if is_code:
                # Data to be taken from the code
                data = dict()
                for name in get_component_names():
                    if name[0] not in EXCLUDE_PREFIXES:
                        # component_info is a tuple, which contains the component class and its manifest info
                        component = make_component(name)
                        data[name] = { "uri" : Url(component.getCodeUri()), "desc" : component.getDesc() }
                """
                data = dict([ (name, { "uri" : Url(component_class().getCodeUri()), "desc" : component_class().getDesc() } ) \
                                    for (name, (component_class, component_config)) in get_code_map().items() \
                                        if name[0] not in EXCLUDE_PREFIXES ])
                """
            else:
                # We are looking for partial resources
                data = listResources(partials=True)
        else:
            # Path elements (the known code prefix is stripped off)
            path_elems = self.request.getRequestPath()[len(prefix):].split("/")[1:]
            if is_code:
                # We are referencing actual components here
                component_name  = path_elems[0]   # This should be the name of the code element
                component_path  = self.request.getRequestPath()
            else:
                # We are looking at a partial resource. Therefore, we need to load
                # that resource and then get the code URI from it.
                specialized_code_name = path_elems[0]
                specialized_code      = retrieveResourceFromStorage(getResourceUri(specialized_code_name, is_partial=True), only_public=False, is_partial=True)
                if not specialized_code:
                    return Result.notFound("Cannot find specialized component resource '%s'" % specialized_code_name)
                component_path        = specialized_code["private"]["code_uri"]
            
            # Instantiate the component
            component = getComponentObjectFromPath(component_path)
            if not component:
                return Result.notFound("Unknown component")
            component_home_uri = component.getCodeUri()

            if is_code:
                self.breadcrumbs.append((component_name, component_home_uri))
            else:
                self.breadcrumbs.append((specialized_code_name, specialized_code["public"]["uri"]))

            if len(path_elems) == 1:
                #
                # No sub-detail specified: We want meta info about a code segment (component)
                #
                data = component.getMetaData()

                #
                # If this is based on a specialized component then we need to overwrite some
                # of the component's meta data with the info from the specialized component
                # definition.
                #
                if not is_code:
                    data = specializedOverwrite(data, specialized_code)

                data = languageStructToPython(component, data)
                if is_code:
                    qs = ""
                    cname = component_name
                else:
                    qs = "?specialized=y"
                    cname = specialized_code_name
                self.context_header.append(("[ Create resource ]", settings.PREFIX_RESOURCE+"/_createResourceForm/form/"+cname+qs, ""))  #, "target=_blank"))
            else:
                #
                # Some sub-detail of the requested component was requested
                #
                sub_name = path_elems[1]
                if sub_name == "doc":
                    data       = component.getDocs()
                    self.breadcrumbs.append(("Doc", component_home_uri + "/doc"))
                else:
                    return Result.notFound("Unknown code detail")
                
        return Result.ok(data)


    def __process_post(self, is_code, prefix):
        """
        Process a POST request.
        
        The only allowed POST requests to code are requests
        to the base URI of a component. This creates a new resource.
        
        Same with spezialiced code.

        @param is_code:     Indicates whether this is a request for un-specialized code.
        @type is_code:      boolean

        @param prefix:      The prefix for this type of request.
        @type prefix:       string

        @return:  HTTP return structure.
        @rtype:   Result

        """
        if is_code:
            # If we are dealing with actual components then the path of this request
            # here is the correct path to find the component class.
            component_path        = self.request.getRequestPath()
            specialized_code_name = None
            specialized_code      = None
        else:
            # But if we are dealing with specialized components then we first need to
            # retrieve the partial resource definition and extract the component path
            # from there.
            path_elems = self.request.getRequestPath()[len(prefix):].split("/")[1:]
            specialized_code_name = path_elems[0]
            specialized_code      = retrieveResourceFromStorage(getResourceUri(specialized_code_name, is_partial=True), only_public=False, is_partial=True)
            if not specialized_code:
                return Result.notFound("Cannot find specialized component resource '%s'" % specialized_code_name)
            component_path        = specialized_code["private"]["code_uri"]

        #
        # Start by processing and sanity-checking the request.
        #
        component = getComponentObjectFromPath(component_path)
        if not component:
            return Result.notFound("Unknown component")
        #component = component_class()
        body = self.request.getRequestBody()
        try:
            param_dict = json.loads(body)
        except Exception, e:
            raise RestxException("Malformed request body: " + str(e))
        ret_msg = makeResourceFromComponentObject(component, param_dict, specialized_code, specialized_code_name)
        # This is returned back to the client, so we should take the URI
        # string and cast it to a Url() object. That way, the DOCUMENT_ROOT
        # can be applied as needed before returning this to the client.
        location = ret_msg['uri']
        ret_msg['uri'] = Url(location)
        return Result.created(location, ret_msg)

    def __process_delete(self, is_code, prefix):
        """
        Process a DELETE request.
        
        The only allowed DELETE here is on specialized component resources.
        
        @param is_code:     Indicates whether this is a request for un-specialized code.
        @type is_code:      boolean

        @param prefix:      The prefix for this type of request.
        @type prefix:       string

        @return:            HTTP return structure.
        @rtype:             Result

        """
        if not is_code:
            try:
                deleteResourceFromStorage(self.request.getRequestPath(), True)
                return Result.ok("Resource deleted")
            except RestxException, e:
                return Result(e.code, str(e))
        else:
            return Result.badRequest("Can only delete specialized component resources")

    
    def process(self):
        """
        Process the request.
        
        @return:  HTTP return structure.
        @rtype:   Result
        
        """
        method = self.request.getRequestMethod()

        # We are also handling requests for specialized code. Let's
        # detect them here and pass our findings to the request handlers.
        if self.request.getRequestPath().startswith(settings.PREFIX_CODE):
            is_code = True
            prefix  = settings.PREFIX_CODE
        else:
            is_code = False
            prefix  = settings.PREFIX_SPECIALIZED

        if method == HTTP.GET_METHOD:
            return self.__process_get(is_code, prefix)
        elif method == HTTP.POST_METHOD:
            return self.__process_post(is_code, prefix)
        elif method == HTTP.DELETE_METHOD:
            return self.__process_delete(is_code, prefix)

