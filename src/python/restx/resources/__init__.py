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
Here we have all the defintions and implementations
for resource storage and access.

Storage is VERY simple at this point: We take the
unique name of the resource (also the last path element
of the resource's URI) as the filename under which we
store a JSON representation of the resource.

The stored representation of a resource looks like this:

    {
        "public": {
                    .... what a client can see, usually
                    the name, uri, description, sub_resources
                    and any available runtime-parameters.
                    This dictionary is returned when a
                    client requests information about a resource.
                  },
        "private": {
                    ... what was provided when the resource was
                    defined.
                   }
    }

"""

# Python imports
import os
import copy

# RESTx imports
import restx.components
import restx.core.codebrowser
import restx.settings as settings

from restx.platform_specifics     import STORAGE_OBJECT
from restx.logger                 import *
from restx.core.parameter         import TYPE_COMPATIBILITY, PARAM_STRING_LIST, PARAM_NUMBER_LIST
from restx.languages              import *

from org.mulesoft.restx.exception import *
from org.mulesoft.restx.util      import Url


EXCLUDED_NAMES = [ "readme.txt" ]
EXCLUDE_PREFIXES = [ "_" ]


def getResourceUri(resource_name, is_partial=False):
    """
    Construct a resource's URI based on its name.

    @param is_partial:  Indicates whether this is a partial resource.
    @type is_partial:   boolean

    @return:            URI of the named resource.
    @rtype:             string
    
    """
    if is_partial:
        return settings.PREFIX_SPECIALIZED + "/" + resource_name
    else:
        return settings.PREFIX_RESOURCE + "/" + resource_name


def retrieveResourceFromStorage(uri, only_public=False, is_partial=False):
    """
    Return the details about a stored resource (partial or otherwise).
    
    The resource is identified via its URI.
    
    @param uri:         Identifies a resource via its URI.
    @type  uri:         string
    
    @param only_public: Flag indicating whether we only want to see the
                        public information about this resource.
    @type only_public:  boolean

    @param is_partial:  Indicate whether we are loading a partial resource.
    @type is_partial:   boolean
    
    @return:            Dictionary or None if not found.
    @rtype:             dict
    
    """
    # Need to take the resource URI prefix off to get the resource_name.
    if is_partial:
        resource_name = uri[len(settings.PREFIX_SPECIALIZED)+1:]
    else:
        resource_name = uri[len(settings.PREFIX_RESOURCE)+1:]
    obj = None
    try:
        obj = STORAGE_OBJECT.loadResourceFromStorage(resource_name, is_partial)
        if not obj:
            raise Exception("Unknown resource: " + resource_name)
        if type(obj) is not dict  or  'public' not in obj:
            obj = None
            raise Exception("Missing top-level element 'public' or malformed resource.")
        public_obj = obj['public']
        # Do some sanity checking on the resource. Needs to contain
        # a few key elements at least.
        for mandatory_key in [ 'uri', 'desc', 'name' ]:
            if mandatory_key not in public_obj:
                public_obj = None
                raise Exception("Mandatory key '%s' missing in stored resource '%s'" % \
                                (mandatory_key, resource_name))
        if only_public:
            obj = public_obj
            
    except Exception, e:
        log("Malformed storage for resource '%s': %s" % (resource_name, str(e)), facility=LOGF_RESOURCES)
    return obj


def deleteResourceFromStorage(uri, is_partial=False):
    """
    Delete a resource definition from storage.

    @param uri:   Uri of the resource
    @type  uri:   string

    """
    resource_name = uri[len(settings.PREFIX_SPECIALIZED if is_partial else settings.PREFIX_RESOURCE)+1:]
    STORAGE_OBJECT.deleteResourceFromStorage(resource_name, is_partial)

def listResources(partials=False):
    """
    Return list of all stored resources.
    
    Data is returned as dictionary keyed by resource name.
    For each resource the complete URI, the name and the description
    are returned.

    @param partials:     Indicate whether we want to list the partial resources
    @type partials:      boolean
    
    @return: Dictionary of available resources.
    @rtype:  dict
    
    """
    dir_list = STORAGE_OBJECT.listResourcesInStorage(partials)
    out = {}
    for resource_name in dir_list:
        rname = resource_name.lower()
        if rname not in EXCLUDED_NAMES  and  rname[0] not in EXCLUDE_PREFIXES:
            resource_dict = retrieveResourceFromStorage(getResourceUri(resource_name, partials), only_public=True, is_partial=partials)
            if resource_dict:
                out[resource_name] = dict(uri=Url(resource_dict['uri']), desc=resource_dict['desc'])
            else:
                out[resource_name] = "Not found"
    return out


def paramSanityCheck(param_dict, param_def_dict, name_for_errors, make_specialized=False):
    """
    Check whether a provided parameter-dict is compatible
    with a parameter-definition-dict.
    
    The following checks are performed:
    
     * Are there any keys in the params that are not in the definition?
     * Are all required parameters present?
     * Are the types compatible?
    
    Does not return anything but raises RestxException with
    meaningful error message in case of problem.
    
    The 'name_for_errors' is used in the error message and provides
    some context to make the error message more useful.
    
    @param param_dict:       The parameter dictionary provided (for example by the client).
    @type  param_dict:       dict
    
    @param param_def_dict:   The parameter definition as provided by the component (the code).
                             The provided parameters are checked against this definition.
    @type  param_def_dict:   dict
    
    @param name_for_errors:  A section name, which helps to provide meaningful error messages.
    @type  name_for_errors:  string

    @param make_specialized: Indicates whether we are creating a specialized component resource.
                             In that case, we allow mandatory parameters to remain unset.
    @type  make_specialized: boolean
    
    @raise RestxException:   If the sanity check fails.
    
    """
    #
    # Check whether there are unknown parameters in the 'param' section
    # and also whether the type is compatible.
    #
    if param_dict  and  type(param_dict) is not dict:
        raise RestxException("The '%s' section has to be a dictionary" % name_for_errors)
    if param_def_dict  and  param_dict:
        for pname in param_dict:
            # Any unknown parameters
            if pname not in param_def_dict:
                continue                            # JBJB todo
                raise RestxBadRequestException("Unknown parameter in '%s' section: %s" % (name_for_errors, pname))
            # Sanity check the types
            type_str    = param_def_dict[pname]['type']
            param_value = param_dict[pname]
            param_type  = type(param_value)
            storage_types, runtime_types, conversion_func = TYPE_COMPATIBILITY[type_str]
            choices     = param_def_dict[pname].get('val_choices')
            multi_choice = False
                
            if choices:
                str_choices = [ str(c) for c in choices ]
                if param_type is list:
                    multi_choice = True
                    # Multi choice box and multiple choices were specified by client
                    for val in param_value:
                        if str(val) not in str_choices:
                            raise RestxBadRequestException("List value '%s' for parameter '%s' is not one of the permissible choices." % (str(val), pname))
                else:
                    if str(param_value) not in str_choices:
                        raise RestxBadRequestException("Value '%s' for parameter '%s' is not one of the permissible choices." % (str(param_value), pname))

            if param_type in runtime_types  and  param_type is not list:
                # No type conversion necessary
                pass
            elif param_type not in storage_types  or  param_type is list:
                # Need to perform some type conversion (always needs to be done for lists, since each element
                # needs to go through the conversion.
                val = None
                try:
                    if conversion_func:
                        val = conversion_func(param_value)
                    else:
                        raise Exception("Cannot convert provided parameter type (%s) to necessary type(s) '%s'" % \
                                        (param_type, runtime_types))
                except Exception, e:
                    raise RestxBadRequestException("Incompatible type for parameter '%s' in section '%s': %s" % \
                                                   (pname, name_for_errors, str(e)))
                    
    #
    # Check whether all required parameters are present. This check
    # is skipped for specialized component resources, since the users
    # of those resources need to provide missing parameters when they
    # create the 'normal' resources later on.
    #
    if not make_specialized:
        for pname, pdict in param_def_dict.items():
            if pdict['required']  and  (not param_dict  or  pname not in param_dict):
                raise RestxMandatoryParameterMissingException("Missing mandatory parameter '%s' in section '%s'" % (pname, name_for_errors))

def fillDefaults(param_def_dict, param_dict):
    """
    Copy defaults values into parameter dictionary if not present.
    
    The parameter dictionaries may be defined with defaults.
    So, if the param_dict does not contain anything for those
    parameters then we will create them in there with the
    default value that were specified in the parameter definition.
    
    @param param_def_dict:  The parameter definition- including default values -
                            provided by the component code.
    @type  param_def_dict:  dict
    
    @param param_dict:      The parameter definition provided by the client.
    @type  param_dict:      dict
    
    """
    for pname, pdict in param_def_dict.items():
        if not pdict['required']  and  pname not in param_dict:
            if pdict['default'] is not None:
                if param_def_dict[pname]['type'] in [ PARAM_STRING_LIST, PARAM_NUMBER_LIST ]:
                    param_dict[pname] = [ pdict['default'] ]
                else:
                    param_dict[pname] = pdict['default']

def convertTypes(param_def_dict, param_dict):
    """
    Convert parameters to those types indicated in the parameter definition.

    This is useful when we get parameters, such as the URL command line, where
    all is passed as string.

    @param param_def_dict:  The parameter definition- including default values -
                            provided by the component code.
    @type  param_def_dict:  dict
    
    @param param_dict:      The parameter definition provided by the client.
    @type  param_dict:      dict

    """
    for pname in param_dict:
        if pname in param_def_dict:
            # Only do this when we know about the parameter. Ignore parameters that
            # we don't know about.
            type_str   = param_def_dict[pname]['type']
            param_val  = param_dict[pname]
            param_type = type(param_val)
            storage_types, runtime_types, conversion_func = TYPE_COMPATIBILITY[type_str]
            if param_type in runtime_types  and  param_type is not list:
                pass
            elif param_type not in storage_types  or  param_type is list:
                # Lists always need to undergo type conversion, since we need to perform the
                # check for every element in the list
                try:
                    if conversion_func:
                        param_dict[pname] = conversion_func(param_val)
                        if param_dict[pname] is None:
                            raise Exception("Cannot convert one of the provided list elements to the necessary type.")
                    else:
                        raise Exception("Cannot convert provided parameter type (%s) to necessary type(s) '%s'" % \
                                        (param_type, runtime_types))
                except Exception, e:
                    raise RestxBadRequestException("Incompatible type for parameter '%s': %s" % (pname, str(e)))


def specializedOverwrite(component_meta_data, specialized_component_data):
    """
    Combine component's meta data with specified data of specialized component data.

    Overwrites the desc, name and uri of the component meta data with the
    data appropriate for the specialized component (a partial resource definition).
    Removes the 'specialized' parameter from the 'resource_creation_params'.

    Also adds the 'is_settable = False' flag to parameters that have been defined
    in the partial resource definition, so that the client can see that these
    parameters cannot be provided anymore.

    Adds a noticeable string in the 'default' value for those parameters as well.

    @param component_meta_data:         The meta data as returned by the component.
    @type component_meta_data:          dict

    @param specialized_component_data:  The partial resource defintion for this specialized component.
    @type specialized_component_data:   dict

    @return:                            Updated component meta data.
    @rtype:                             dict

    """
    component_meta_data['desc'] = specialized_component_data['public']['desc']
    component_meta_data['name'] = specialized_component_data['public']['name']
    component_meta_data['uri']  = specialized_component_data['public']['uri']
    component_meta_data['doc']  = specialized_component_data['public']['uri'] + "/doc"
    try:
        rcp = specialized_component_data['private']['resource_creation_params']
    except:
        rcp = None
    if rcp:
        component_meta_data['resource_creation_params']['desc']['default'] = rcp['desc']
        del component_meta_data['resource_creation_params']['specialized']   # Cannot create specialized resources from this one
        data_params        = component_meta_data['params']
        specialized_params = specialized_component_data['private']['params']
        for pname in specialized_params:
            data_params[pname]['default'] = "*** PROVIDED BY COMPONENT SPECIALIZATION ***"
            data_params[pname]['is_settable'] = False

    return component_meta_data


def makeResourceFromComponentObject(component, params, specialized=None, partial_resource_name=None):
    """
    Create a new resource representation from the
    specified component class and parameter dictionary
    and store it on disk.
        
    The parameters need to look something like this:
    
            {
                "reource creation_params" : {
                        "suggested_name" : "my_twitter",
                        "desc"           : "Our Twitter stream",
                        "specialized"    : false
                },
                "params" : {
                        "user"     : "AccountName",
                        "password" : "some password"
                },
            }

    The method performs sanity checking on the supplied
    parameters and also fills in default values where
    available.
    
    @param component_class: A class (not instance) derived from BaseComponent.
    @type  component_class: BaseComponent or derived.
    
    @param params:          The resource parameters provided by the client.
                            Needs to contain at least a 'params' dictionary
                            or a 'resource_creation_dictionary'. Can contain
                            both.
    @type  params:          dict

    @param specialized:     If this resource should be based on a partial resource
                            definition (specialized code) then we are given the
                            resource definition dictionary of the partial resource
                            here. Otherwise, this is None. This is only permitted
                            if the resource-creation-parameters do NOT set the
                            'specialized' flag. That flag indicates that we want
                            to create a new specialized component resource, not a resource
                            based on a specialized component.
    @type specialized:      dict

    @param partial_resource_name: Name of the partial resource from which we have the
                                  specialized (partial resource) definition.
    @type partial_resource_name:  string
    
    @return:                Success message in form of dictionary that contains
                            "status", "name" and "uri" fields.
    @rtype:                 dict
    
    @raise RestxException:  If the resource creation failed or there was a
                            problem with the provided parameters.

    """    
    # We get the meta data (parameter definition) from the component
    component_params_def = component.getMetaData()
    component_params_def = languageStructToPython(component, component_params_def)
    if specialized:
        # Do an overwrite and merge with the specialized component (partial resource
        # data). This may modify the description and suggested name defaults.
        component_params_def = specializedOverwrite(component_params_def, specialized)

    #
    # First we check whether there are any unknown parameters specified
    # on the top level.
    #
    if type(params) is not dict:
        raise RestxException("Malformed resource parameter definition. Has to be JSON dictionary.")
        
    for k in params.keys():
        if k not in [ 'params', 'resource_creation_params' ]:
            raise RestxBadRequestException("Malformed resource parameter definition. Unknown key: %s" % k)

    # Check whether there are unknown parameters in the 'param' or 'resource_creation_params' section.
    provided_params = params.get('params')

    if not provided_params:
        # If no parameters were provided at all, we create them as
        # an empty dictionary. We need something here to be able
        # to merge some defaults into it later on.
        provided_params = dict()
        params['params'] = provided_params

    # Merge with any parameters provided by a partial resource we may use as base
    # If there are doubles (something was provided with the create request, which was
    # also already defined in the partial base resource) then we are simply ignoring
    # the provided value and overwrite them with what was defined in the partial
    # resource.
    specialized_params = None
    if specialized:
        try:
            specialized_params  = specialized['private']['params']
            provided_params.update(specialized_params)
        except:
            pass

    provided_resource_creation_params = params.get('resource_creation_params')
    # Note the difference between 'specialized' and the 'make_specialized_component' flag:
    # If a 'specialized' parameter is provided then we know that we want to create a new
    # usable resource, based on a specialized component resource. However, if the
    # resource-creation-parameters contain the 'specialized' flag, this means that we
    # just want to create the specialized component resource (the base resource). Those
    # two things are mutually exclusive.
    if provided_resource_creation_params:
        make_specialized_component = provided_resource_creation_params.get('specialized', False)
        if make_specialized_component and specialized:
            raise RestxException("Cannot create resource with specializec component resource as base AND set 'specialized' flag at the same time.")
    else:
        make_specialized_component = False
    paramSanityCheck(provided_params, component_params_def['params'], 'params', make_specialized_component)
    paramSanityCheck(provided_resource_creation_params,
                     component_params_def['resource_creation_params'],
                     'resource_creation_params')
    # Before storing the parameters, we make sure they are converted to the
    # types that have been specified
    convertTypes(component_params_def['params'], provided_params)

    # The parameters passed the sanity checks. We can now create the resource definition.
    suggested_name = provided_resource_creation_params['suggested_name']
    resource_uri   = (settings.PREFIX_RESOURCE if not make_specialized_component else settings.PREFIX_SPECIALIZED) + "/" + suggested_name
    resource_name  = suggested_name # TODO: Should check if the resource exists already...
    params['code_uri'] = component.getCodeUri()  # Need a reference to the code that this applies to
    
    # Some parameters are optional. If they were not supplied,
    # we need to add their default values. However, we only do this
    # when we create a normal resource. For specialized component
    # resources, we don't want to set those default values, since
    # otherwise they appear as 'set and unmodifiable' for those
    # who want to create an actual resource based on a specialized
    # component resource.
    if not make_specialized_component:
        fillDefaults(component_params_def['params'], provided_params)
    fillDefaults(component_params_def['resource_creation_params'], provided_resource_creation_params)

    # After all parameters have been dealt with, we now
    # should remove all the parameters that came from a partial resource
    # if we are creating a component based on that.
    private_params = params.get('params')
    if specialized_params  and  private_params:
        for key in specialized_params.keys():
            if key in private_params:
                del private_params[key]

    # Storage for a resource contains a private and public part. The public part is what
    # any user of the resource can see: URI, name and description. In the private part we
    # store whatever was provided here during resource creation. It contains the information
    # we need to instantiate a running resource.
    resource_def = {
        "private" : params,
        "public"  : {
                        "uri"  : resource_uri,
                        "name" : resource_name,
                        "desc" : provided_resource_creation_params['desc']
                    }
    }
    if specialized:
        resource_def['extends'] = partial_resource_name
        del resource_def['private']['code_uri']
    
    # Storage to our 'database'.
    STORAGE_OBJECT.writeResourceToStorage(resource_name, resource_def, make_specialized_component)

    # Send a useful message back to the client.
    success_body = {
        "status" : "created",
        "name"   : resource_name,   # Is returned, because server could have chosen different name
        "uri"    : resource_uri
    }

    return success_body

    
def makeResource(component_name, params, specialized=False):
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
    if specialized:
        specialized_code      = retrieveResourceFromStorage(getResourceUri(component_name, is_partial=True), only_public=False, is_partial=True)
        if not specialized_code:
            raise RestxResourceNotFoundException("Cannot find specialized component resource '%s'" % component_name)
        component_path        = specialized_code["private"]["code_uri"]
        component             = restx.core.codebrowser.getComponentObjectFromPath(component_path)
        specialized_code_name = component_name
    else:
        component             = restx.components.make_component(component_name)
        specialized_code      = None
        specialized_code_name = None

    return makeResourceFromComponentObject(component, params, specialized_code, specialized_code_name)

