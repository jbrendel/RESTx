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
import urlparse, urllib, urllib2, socket, httplib, base64

import restx.settings as settings

from restx.storageabstraction.file_storage import FileStorage
from org.mulesoft.restx.component          import BaseComponentCapabilities
from org.mulesoft.restx.component.api      import HttpResult, HTTP

_ACCESS_RESOURCE_IMPORTED = False

class BaseCapabilities(BaseComponentCapabilities):
    """
    This implements some of the base capabilities, which the framework
    makes available to components of any language. Implemented in Python,
    but by inheriting from a Java interface, it is just as usable from
    within Java.
    
    """
    def __init__(self, component):
        self.__accountname   = None
        self.__password      = None
        self.__my_component  = component

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
        my_resource_name = self.__my_component.getMyResourceName()
        if my_resource_name:
            if namespace:
                unique_namespace = "%s__%s" % (self.__my_component.getMyResourceName(), namespace)
            else:
                unique_namespace = self.__my_component.getMyResourceName()
            storage = FileStorage(storage_location=settings.STORAGEDB_LOCATION, unique_prefix=unique_namespace)
            return storage
        else:
            # Cannot get storage object when I am not running as a resource
            return None
    
    def __get_http_opener(self, url):
        """
        Return an HTTP handler class, with credentials enabled if specified.
        
        @param url:    URL that needs to be fetched.
        @type url:     string
        
        @return:       HTTP opener (from urllib2)
        
        """
        if self.__accountname  and  self.__password:
            passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
            passman.add_password(None, url, self.__accountname, self.__password)
            authhandler = urllib2.HTTPBasicAuthHandler(passman)
            opener = urllib2.build_opener(authhandler)
        else:
            opener = urllib2.build_opener()
        return opener
        
    def httpSetCredentials(self, accountname, password):
        """
        The component author can set credentials for sites that require authentication.
        
        @param accountname:    Name of account
        @type accountname:     string
        
        @param password:       Password for account.
        @type password:        string
        
        """
        self.__accountname = accountname
        self.__password    = password
    
    def __http_access(self, method, url, data=None, headers=None, timeout=None):
        """
        Access an HTTP resource with GET or POST.
        
        @param method:     The method for the HTTP request
        @type method:      string
        
        @param url:        The URL to access.
        @type url:         string
        
        @param data:       If present specifies the data for a POST request.
        @type data:        Data to be sent or None.
        
        @param headers:    A dictionary of additional HTTP request headers.
        @type headers:     dict

        @param timeout:    Timeout for the request in seconds, or None.
        @type timeout:     float
        
        @return:           Code and response data tuple.
        @rtype:            tuple
        
        """
        (scheme, host_port, path, params, query, fragment) = urlparse.urlparse(url)
        path        = urllib.quote(path)
        query       = urllib.quote_plus(query, safe="=&")
        allpath     = path + (("?%s" % query) if query else "") + (("#%s" % fragment) if fragment else "")
        host, port  = urllib.splitport(host_port)

        if headers:
            if type(headers) is not type(dict):
                # If this was called from Java then the headers are
                # defined in a HashMap. We need to translate that to
                # a Python dictionary.
                header_dict = dict()
                header_dict.update(headers)
                headers = header_dict
        else:
            headers = dict()

        #
        # For some reason, under Jython we are REALLY slow in handling the kind
        # of host names where we get more than one DNS hit back.
        #
        # As a stop gap measure:
        #
        #    1. Do a normal DNS lookup for the host name, using the socket library
        #    2. Replace the host name in the URI with the IP address string
        #    3. Add a 'Host' header with the original host name to the request
        #
        # Wish I wouldn't have to do that...
        #
        try:
            ipaddr          = socket.gethostbyname(host)   # One of the possible IP addresses for this host
            headers["Host"] = host                         # Will add a proper host header
            host            = ipaddr
        except Exception, e:
            # Can't do IP address replacemenet? Let it sort itself out on its own
            pass

        if (self.__accountname is not None)  and  (self.__password is not None):
            headers["Authorization"] = "Basic " + base64.encodestring('%s:%s' % (self.__accountname, self.__password))[:-1]

        if scheme == 'https':
            conn = httplib.HTTPSConnection(host)
        else:
            conn = httplib.HTTPConnection(host)

        conn.request(method, allpath, data, headers)
        conn.sock.settimeout(timeout)

        try:
            resp   = conn.getresponse()
            code   = resp.status
            data   = resp.read()
        except socket.timeout, e:
            return HTTP.REQUEST_TIMEOUT, "Request timed out"

        return code, data
        
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
        
        @return:           HttpResult object.
        @rtype:            HttpResult
        
        """
        res                  = HttpResult()
        res.status, res.data = self.__http_access("GET", url, headers=headers, timeout=timeout)
        return res


    def httpPost(self, url, data, headers=None, timeout=None):
        """
        Send the specified data to the specified URL.
        
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
        
        @return:           HttpResult object.
        @rtype:            HttpResult
        
        """
        res                  = HttpResult()
        res.status, res.data = self.__http_access("POST", url, data, headers, timeout)
        return res

    def accessResource(self, *args, **kwargs):
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
        global _ACCESS_RESOURCE_IMPORTED
        if not _ACCESS_RESOURCE_IMPORTED:
            # Some annoying circular import issued handled this way
            from restx.resources.resource_runner import accessResource as accessResource_glob
            from restx.resources                 import makeResource as makeResource_glob
            _ACCESS_RESOURCE_IMPORTED = False
        return accessResource_glob(*args, **kwargs)

    def makeResource(self, *args, **kwargs):
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
        global _ACCESS_RESOURCE_IMPORTED
        if not _ACCESS_RESOURCE_IMPORTED:
            # Some annoying circular import issued handled this way
            from restx.resources.resource_runner import accessResource as accessResource_glob
            from restx.resources                 import makeResource as makeResource_glob
            _ACCESS_RESOURCE_IMPORTED = False
        return makeResource_glob(*args, **kwargs)

