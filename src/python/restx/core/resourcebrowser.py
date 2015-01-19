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
Allows users and clients to browse the defined resources.
      
"""
# Python imports
import os
import traceback

# RESTx imports
import restx.settings as settings

from org.mulesoft.restx.util            import Url
from org.mulesoft.restx.exception       import *
from org.mulesoft.restx.component.api   import HTTP, HttpMethod, Result

from restx.logger                       import *
from restx.render                       import DEFAULT_OUTPUT_TYPES, RENDERER_ID_SHORTCUTS
from restx.core.basebrowser             import BaseBrowser
from restx.resources                    import paramSanityCheck, fillDefaults, listResources, \
                                               retrieveResourceFromStorage, getResourceUri, deleteResourceFromStorage
from restx.resources.resource_runner    import _accessComponentService, _getResourceDetails

import java.lang.String
import java.lang.Exception


def content_type_match(possible_types, accepted_types):
    """
    Find the first match between possible types and accepted types.

    Note: We make a specific exception for text/html. This is normally
    sent by a browser. If we detect that anywhere (!) in the list of
    accepted content types, then we will give this one priority.

    Throws exception if we can't find a match.

    @param possible_types:      List of possible content types.
    @type possible_types:       list

    @param accepted_types:      List of content types accepted by the client.
    @type accepted_types:       list

    @return                     The best matched content type.
    @rtype:                     string

    """
    if not accepted_types  or  accepted_types[0] == "*/*":
        # If no specific content type was defined with 'Accept' then
        # we will just assume the first one of our specified output types.
        return possible_types[0]

    if "text/html" in accepted_types and "text/html" in possible_types:
        return "text/html"

    for atype in accepted_types:
        if atype in possible_types:
            return atype

    raise RestxNotAcceptableException()


def get_request_query_dict(request, only_params_list=None):
        """
        Return a dictionary of the parsed query arguments.
        
        @param request:           The request object.
        @type  request:           RestxHttpRequest

        @param only_params_list:  Optional list of parameter names. When specified
                                  then we will ignore all parameters that are not
                                  in this list.
        @type  only_params_list:  list
        
        @return:                  Dictionary with query arguments.
        @rtype:                   dict
        
        """
        query_string = request.getRequestQuery()
        if query_string:
            # Parse the query string apart and put values into a dictionary
            runtime_param_dict = dict([elem.split("=") if "=" in elem else (elem, None) \
                                                       for elem in query_string.split("&")])
            if only_params_list:
                runtime_param_dict = dict([ (key, value) for (key, value) in runtime_param_dict.items() if key in only_params_list ])
        else:
            runtime_param_dict = dict()
        return runtime_param_dict

#
# Translates the string representation of the HTTP method to
# the HttpMethod enum type.
#
__HTTP_METHOD_LOOKUP = {
    HTTP.GET_METHOD     : HttpMethod.GET,
    HTTP.POST_METHOD    : HttpMethod.POST,
    HTTP.PUT_METHOD     : HttpMethod.PUT,
    HTTP.DELETE_METHOD  : HttpMethod.DELETE,
    HTTP.HEAD_METHOD    : HttpMethod.HEAD,
    HTTP.OPTIONS_METHOD : HttpMethod.OPTIONS,    
}

class ResourceBrowser(BaseBrowser):
    """
    Handles requests for resource info.
    
    """
    def __init__(self, request):
        """
        Initialize the browser with the render-args we need for meta data browsing.
        
        @param request: Handle to the HTTP request that needs to be processed.
        @type request:  RestxHttpRequest
        
        """
        super(ResourceBrowser, self).__init__(request,
                                              renderer_args = dict(no_annotations=True,
                                                                   no_table_headers=False,
                                                                   no_list_indices=False,
                                                                   no_borders=False))
 

    def process(self):
        """
        Process the request.
     
        @return:  HTTP result structure.
        @rtype:   Result
        
        """
        method = self.request.getRequestMethod()

        if method == HTTP.GET_METHOD:
            # It's the responsibility of the browser class to provide breadcrumbs
            self.breadcrumbs = [ ("Home", "/"), ("Resource", settings.PREFIX_RESOURCE) ]

        if self.request.getRequestPath() == settings.PREFIX_RESOURCE:
            #
            # Request to the base URL of all resources (listing resources)
            #
            if method == HTTP.GET_METHOD:
                #
                # List all the resources
                #
                return Result.ok(listResources())
            else:
                raise RestxMethodNotAllowedException()
            
        else:
            # Path elements (the known resource prefix is stripped off)
            path          = self.request.getRequestPath()[len(settings.PREFIX_RESOURCE):]
            path_elems    = path.split("/")[1:]
            resource_name = path_elems[0]   # This should be the name of the resource base

            # If the path ends with a '/' then there might be an empty element at the end,
            # which we can remove.
            if not path_elems[-1:][0]:
                path_elems.pop()
            
            # Before calling delete on a resource, we have to make sure that this DELETE
            # is just for the resource itself, not a DELETE to some of the sub-services.
            # If it's just for the resource then there will be only one path element (the
            # resource name).
            if method == HTTP.DELETE_METHOD  and  len(path_elems) == 1:
                try:
                    deleteResourceFromStorage(self.request.getRequestPath())
                    return Result.ok("Resource deleted")
                except RestxException, e:
                    return Result(e.code, e.msg)

            # Get the public representation of the resource
            rinfo = _getResourceDetails(resource_name)
            if not rinfo:
                return Result.notFound("Unknown component")
            complete_resource_def = rinfo['complete_resource_def']
            resource_home_uri     = rinfo['resource_home_uri']
            public_resource_def   = rinfo['public_resource_def']
            code_uri              = rinfo['code_uri']
            component             = rinfo['component']
            services              = public_resource_def['services']
            public_resource_def['uri'] = Url(public_resource_def['uri'])

            if method == HTTP.GET_METHOD:
                self.breadcrumbs.append((resource_name, resource_home_uri))

            # Was there more to access?
            if len(path_elems) > 1:
                #
                # Some sub-service of the component was requested. This means
                # we actually need to pass the parameters to the component
                # and call this service function.
                #
                
                service_name = path_elems[1]

                # If the service name contains a "." then we might deal with
                # a content type ID in the URI (used by clients who don't know how
                # to deal with the 'Accept' or 'Content-type' headers properly).
                # In that case, we remove that ID from the service name.
                content_type_from_id = None
                if "." in service_name:
                    service_name, content_id = service_name.split(".")
                    content_type_from_id = RENDERER_ID_SHORTCUTS.get(content_id)
                    self.request.setContentType(content_type_from_id)

                if not content_type_from_id:
                    # Get the supported output content types for this service method
                    requested_content_types = self.request.preferredContentTypes()
                else:
                    # We have a content type specified in the URI
                    requested_content_types = [ content_type_from_id ]

                try:
                    service_def = complete_resource_def['public']['services'][service_name]
                except KeyError, e:
                    raise RestxResourceNotFoundException("Cannot find '%s'." % service_name)

                # This service has some possible runtime parameters defined.
                # We pass this service definition's parameter list in, since that
                # means we are filtering out all those parameters that we are
                # not expecting.
                service_params = service_def.get('params')
                if service_params:
                    # Only_params is the list of defined service parameters. Passing this to
                    # get_request_query_dict() means that all other runtime parameters are
                    # filtered out.
                    only_params = service_params.keys()
                    runtime_param_dict = get_request_query_dict(self.request, only_params)
                else:
                    only_params = None
                    runtime_param_dict = dict()   # No service parameters defined? All runtime parameters are removed (ignored).

                possible_output_types   = service_def.get('output_types')
                if not possible_output_types:
                    # If the service method didn't define any type(s) then we just
                    # indicate the ability to create any of the default types
                    possible_output_types = DEFAULT_OUTPUT_TYPES

                if type(possible_output_types) in [ str, unicode, java.lang.String ]:
                    # Always store the output types in a list, even if the service method just
                    # defined a single one
                    possible_output_types = [ possible_output_types ]

                # See that we can match the accepted to possible types
                matched_type      = content_type_match(possible_output_types, requested_content_types)
                positional_params = path_elems[2:]
                input             = self.request.getRequestBody()
                try:
                    http_method = __HTTP_METHOD_LOOKUP.get(self.request.getRequestMethod().upper(), HttpMethod.UNKNOWN)
                    result      = _accessComponentService(component, complete_resource_def,
                                                          resource_name, service_name, positional_params,
                                                          runtime_param_dict, input, self.request,
                                                          http_method)
                    if result == None  or  type(result) is not Result:
                        result = Result.noContent()
                    else:
                        result.setNegotiatedContentType(matched_type)
                except RestxException, e:
                    result = Result(e.code, e.msg)
                except Exception, e:
                    # The service code threw an exception. We need to log that and return a
                    # normal error back to the user.
                    print traceback.format_exc()
                    log("Exception in component for service '%s': %s" % (service_name, str(e)), facility=LOGF_COMPONENTS)
                    result = Result.internalServerError("Internal server error. Details have been logged...")

                if result.getStatus() != HTTP.NOT_FOUND  and  method == HTTP.GET_METHOD  and  service_name in services:
                    self.breadcrumbs.append((service_name, services[service_name]['uri']))
                    
                return result

            else:
                # No, nothing else. Someone just wanted to know more about the resource.
                if method == HTTP.POST_METHOD:
                    raise RestxMethodNotAllowedException()
                return Result.ok(public_resource_def)
