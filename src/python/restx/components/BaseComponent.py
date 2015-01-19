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
Defines a base class for all components.

"""
# Python imports
import urllib, urllib2
from copy import deepcopy

#RESTx imports
import restx.settings as settings

from restx.languages                       import __javaStructToPython
from restx.core.parameter                  import *
from restx.storageabstraction.file_storage import FileStorage
from restx.render                          import DEFAULT_OUTPUT_TYPES, DEFAULT_INPUT_TYPES
from org.mulesoft.restx.component.api      import HttpResult, HTTP

from org.json                              import JSONException
from org.mulesoft.restx.util               import Url, JsonProcessor

ALLOWABLE_SERVICE_KEYS = [ "desc", "params", "positional_params", "allow_params_in_body", "output_types", "input_types" ]

#
# Utility method.
#
def _change_params_to_plain_dict(param_dict):
    """
    Unwraps all the parameter definitions into a plain dictionary.
    
    Needed for browsing or accessing the meta info.
    
    @param param_dict: Dictionary of parameter definitions, with each
                       individual parameter represented by a ParameterDef object.
    @type param_dict:  dict or ParameterDef objects
    
    @return:           Plain dictionary.
    @rtype:            dict
    
    """
    d = dict()
    for name in param_dict.keys():
        d[name] = param_dict[name].as_dict()
    return d


class BaseComponent(object):
    """
    The base class for all code components.
    
    A component author only needs to override a few methods or data values
    to get started.
    
    Specifically:
    
        NAME
        PARAM_DEFINITION
        DESCRIPTION
        DOCUMENTATION
        SERVICES
        
    A component specifies 'sub-SERVICES'. To do so, implement any number of services
    methods. Then list those methods in the 'SERVICES' dictionary (use any name as
    key to a tuple containing the method itself as well as a doc string). Then your
    additional methods will be exposed as sub-services, which can be accessed
    like this: <resource_uri>/<sub_service_method>/....

    The name of the sub-service method is directly specified in the URI.
    
    """
    LANGUAGE         = "PYTHON"
    
    NAME             = ""
    """The name used to refer to this component. Also used to construct its URL. No spaces allowed."""
    PARAM_DEFINITION = dict()
    """The parameter definition in the form of a dictionary."""
    DESCRIPTION      = ""
    """A short, one line description."""
    DOCUMENTATION    = ""
    """Longer, man-page style documentation."""
    SERVICES         = None
    """A dictionary keying method name to docstring for exposed sub-service methods. May be left empty."""
    
    def __init__(self):
        self.__resource_name     = None
        self.__http_request      = None
        self.__base_capabilities = None
        self._instance_conf      = None

        #
        # Fill in some default values in various places
        #

        # The output types of services, which don't specify their own output types
        # should be set to the default types. Same with the input types.
        for sname, sdef in self.SERVICES.items():
            if "output_types" not in sdef:
                sdef["output_types"] = DEFAULT_OUTPUT_TYPES
            if "input_types" not in sdef:
                sdef["input_types"] = DEFAULT_INPUT_TYPES
            elif sdef['input_types'] is None  or  sdef['input_types'] == []:
                # If None or an empty list was defined for input types
                # then we remove them from the dictionary.
                sdef['input_types'] = None
            elif type(sdef['input_types']) in [ str, unicode ]:
                # We can also specify the input type as a single value (not a list).
                # In that case, we transcribe it into a single-element list, so that
                # code using the API always can deal with it in the same way.
                sdef['input_types'] = [ sdef['input_types'] ]
        
    def setInstanceConf(self, instance_conf):
        self._instance_conf = instance_conf;
        self.NAME           = instance_conf['cname']

    def setBaseCapabilities(self, base_capabilities):
        self.__base_capabilities = base_capabilities

    def setResourceName(self, resource_name):
        self.__resource_name = resource_name
        
    def setRequest(self, request):
        self.__http_request = request
        
    def getRequestUri(self):
        return self.__http_request.getRequestURI()

    def getRequestHeaders(self):
        return self.__http_request.getRequestHeaders()
    
    def getMyResourceName(self):
        return self.__resource_name

    def getMyResourceUri(self):
        return "%s/%s" % (settings.PREFIX_RESOURCE, self.getMyResourceName())

    def getFileStorage(self, namespace=""):
        """
        Return a FileStorage object, which can be used to store data.

        Storage spaces for each resource are separated by resource name,
        this means that two resources cannot share their stored objects,
        even if they are of the same type.

        @param namespace:   A namespace that is used by this resource.
                            Per invocation a resource may chose to create
                            yet another resource namespace under (or within)
                            its inherent namespace.
        @type namespace:    string

        @return:            FileStorage object.

        """
        return self.__base_capabilities.getFileStorage(namespace)

    def fromJson(self, str):
        try:
            obj = JsonProcessor.loads(str)
        except JSONException, e:
            raise RestxException("Could not de-serialize data: " + e.getMessage());
        return __javaStructToPython(obj)

    def toJson(self, obj):
        try:
            return JsonProcessor.dumps(obj)
        except JSONException, e:
            raise RestxException("Could not serialize data: " + e.getMessage());
    
    def httpSetCredentials(self, accountname, password):
        """
        The component author can set credentials for sites that require authentication.
        
        @param accountname:    Name of account
        @type accountname:     string
        
        @param password:       Password for account.
        @type password:        string
        
        """
        return self.__base_capabilities.httpSetCredentials(accountname, password)
    
    def httpGet(self, url, headers=None, timeout=None):
        """
        Accesses the specified URL.
        
        If credentials have been specified, they will be used in case
        of HTTP basic authentication.
        
        @param url:        The URL to be accessed.
        @type url:         string
        
        @param headers:    A dictionary of additional HTTP request headers.
        @type headers:     dict

        @param timeout:    Timeout for the request in seconds, or None.
        @type timeout:     float
        
        @return:           Status and data as tuple.
        @rtype:            tuple
        
        """
        res = self.__base_capabilities.httpGet(url, headers=headers, timeout=timeout)
        return (res.status, res.data)
    
    def httpPost(self, url, data, headers=None, timeout=None):
        """
        Send the specified data to the specified URL with the POST method.
        
        If credentials have been specified, they will be used in case
        of HTTP basic authentication.
        
        @param url:        The URL to be accessed.
        @type url:         string
        
        @param data:       The data to be sent to the URL.
        @type data:        string
        
        @param headers:    A dictionary of additional HTTP request headers.
        @type headers:     dict
        
        @param timeout:    Timeout for the request in seconds, or None.
        @type timeout:     float
        
        @return:           Status and data as tuple.
        @rtype:            tuple
        
        """
        res = self.__base_capabilities.httpPost(url, data, headers, timeout=timeout)
        return (res.status, res.data)

    def accessResource(self, resource_uri, input=None, params=None, method=HTTP.GET):
        """
        Access a resource identified by its URI.

        @param resource_name:    The uri of the resource. We allow absolute URIs (well, later at least),
                                 and relative URIs (starting with "/resource/").
                                 Contains resource name, service name and any positional parameters.
        @type resource_name:     string
        
        @param service_name:     Name of the desired service
        @type service_name:      string
        
        @param input:            Any input information that may have been sent with the request body.
        @type input:             string
        
        @param params:           Any run-time parameters for this service as key/value pairs.
        @type params:            dict
        
        @param method:           The HTTP method to be used.
        @type method:            HttpMethod
        
        """
        return self.__base_capabilities.accessResource(resource_uri, input, params, method)

    def makeResource(self, component_name, params, specialized=False):
        """
        Create a new resource representation from the
        component class specified by its name and the parameter
        dictionary and store it on disk.

        Finds the class and then calls makeResourceFromComponentObject()

        @param component_name:  Name of a class derived from BaseComponent.
        @type  component_name:  BaseComponent or derived.
        
        @param params:          The resource parameters provided by the client.
                                Needs to contain at least a 'params' dictionary
                                or a 'resource_creation_dictionary'. Can contain
                                both.
        @type  params:          dict

        @param specialized:     Flag indicates whether this is based on a specialized
                                component resource. In which case the params can be
                                partial and 'component_name' really refers to the name
                                of the specialized component resource.
        @type  specialized:     boolean
        
        @return:                Success message in form of dictionary that contains
                                "status", "name" and "uri" fields.
        @rtype:                 dict
        
        @raise RestxException:  If the resource creation failed or there was a
                                problem with the provided parameters.

        """
        return self.__base_capabilities.makeResource(component_name, params, specialized)

    def getMetaData(self):
        """
        Return meta data about this code.
        
        Contains name, description, documentation URI and parameter
        definitions as dictionary.
        
        @return: Meta info about the component.
        @rtype:  dict
        
        """
        d = dict(uri    = Url(self.getCodeUri()),
                 name   = self.getName(),
                 desc   = self.getDesc(),
                 doc    = Url(self.getCodeUri() + "/doc"),
                 params = _change_params_to_plain_dict(self.getParams()),
                 services = self._getServices()
                )
        #
        # There is also a set of resource meta parameters that always remain
        # the same. Just some of the defaults and descriptions may change
        # from component to component.
        #
        rp = dict(suggested_name = ParameterDef(PARAM_STRING,
                                                "Can be used to suggest the resource name to the server",
                                                required=True),
                  desc           = ParameterDef(PARAM_STRING,
                                                "Specifies a description for this new resource",
                                                required=False, default="A '%s' resource" % self.getName()),
                  specialized    = ParameterDef(PARAM_BOOL,
                                                "Specifies if we want to create a specialized component resource (true) or a normal resource (false)",
                                                required=False, default=False)
                 )
        d['resource_creation_params'] = _change_params_to_plain_dict(rp)
        return d
    
    def getName(self):
        """
        Return the name of the component.
        
        @return:  Name
        @rtype:   string
        
        """
        if self.NAME:
            return self.NAME
        else:
            raise RestxException("Component instance config has not been set, yet.")

    def getDesc(self):
        """
        Return the brief description string of the component.
        
        @return:  Description.
        @rtype:   string
        
        """
        return self.DESCRIPTION
    
    def getDocs(self):
        """
        Return the documentation text for this component.
        
        @return:  Documentation.
        @rtype:   string
        
        """
        return self.DOCUMENTATION

    def getCodeUri(self):
        """
        Return the URI for this component.
        
        @return: URI for the component.
        @rtype:  string
        
        """
        return settings.PREFIX_CODE + "/" + self.getName()
    
    def getParams(self):
        """
        Return the parameter definition for this component.
        
        @return: Parameter definition.
        @rtype:  dict (of ParameterDef objects)
        
        """
        return self.PARAM_DEFINITION

    
    #
    # -------------------------------------------------------------------------------------
    # Following are some methods that are used by the framework and that are not part
    # of the official component-API.
    # -------------------------------------------------------------------------------------
    #
    def _getServices(self, resource_base_uri=None):
        """
        Return a dictionary with the exposed services.
        
        Keyed by name, for each service we return the uri and short description
        and service-specific parameter definition.
        
        @param resource_base_uri:  The base URI for the resource in which the services are
                                   exposed. The base URI through which services are accessed
                                   is the one of the resource (not of this code). Therefore,
                                   if we want the URI of the services in the context of the
                                   resource then we can call this method here with the base
                                   URI of the resource passed in.
        @type resource_base_uri:   string
        
        @return:                   Dictionary with sub-service info.
        @rtype:                    dict
        
        """
        if resource_base_uri:
            base_uri = resource_base_uri
        else:
            # No base URI specified? Then we can get the service URIs relative to
            # the code's URI.
            base_uri = self.getCodeUri()
        if self.SERVICES:
            ret = dict()
            for name in self.SERVICES.keys():
                ret[name]  = deepcopy(self.SERVICES[name])  # That's a dictionary with params definitions and descs
                # Sanity check the service definition
                for key in ret[name].keys():
                    if key not in ALLOWABLE_SERVICE_KEYS:
                        raise RestxException("Unknown key '%s' in description for service '%s'. Only allowed keys are: %s" % (key, name, ', '.join(ALLOWABLE_SERVICE_KEYS)))
                        
                # Create proper dict representations of each parameter definition
                if 'params' in ret[name]:
                    for pname in ret[name]['params'].keys():
                        if type(ret[name]['params'][pname]) is ParameterDef:
                            # Need the type check since we may have constructed the
                            # representation from storage, rather than in memory.
                            # If it's from storage then we don't have ParameterDefs
                            # in this dictionary here, so we don't need to convert
                            # anything.
                            ret[name]['params'][pname] = ret[name]['params'][pname].as_dict()
                ret[name]['uri'] = Url(base_uri + "/" + name)
            return ret
            #return dict([(name, dict(uri=base_uri + "/" + name, desc=self.SERVICES[name])) for name in self.SERVICES.keys() ])
        else:
            return None

