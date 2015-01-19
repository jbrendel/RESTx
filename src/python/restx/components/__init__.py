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
Exports the various components, which are available.

Also defines a base class for all components.

"""
# Import all the components
import restx_components_list

__CODE_MAP         = None
__KNOWN_COMPONENTS = None

def make_component(component_name):
    """
    Return a readily created component. The instance configuration
    (the information from the manifest file) is sent to the component
    as well.

    Returns nothing if the component wasn't found.

    """
    try:
        component_class, component_config = __CODE_MAP[component_name]
        comp = component_class()
        comp.setInstanceConf(component_config)
        return comp
    except KeyError, e:
        return None

def get_component_names():
    """
    Return a list of component names.

    The values are class/config tuples, where 'config' is the content
    of the manifest file.

    """
    global __CODE_MAP, __KNOWN_COMPONENTS
    new_component_list = restx_components_list.import_all()
    if new_component_list:
        __KNOWN_COMPONENTS = new_component_list
        __CODE_MAP         = dict([ (component_config['cname'], (component_class, component_config)) for component_class, component_config in __KNOWN_COMPONENTS ])
    return __CODE_MAP.keys()

