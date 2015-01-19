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

import os
import restx.settings as settings

__IMPORT_COMPLETE = False

__LANG_PY   = "python"
__LANG_JAVA = "java"
__LANG_JAVASCRIPT = "javascript"

__KNOWN_LANGUAGES    = [ __LANG_PY, __LANG_JAVA, __LANG_JAVASCRIPT ]

__MANIFEST_EXTENSION = ".cmfs"

#
# The tokens of the per-component config file and a small validation function for each of them
# along with a generic error message.
#
__KNOWN_CONFIG_TOKENS = {
    "ENABLED" : ( lambda val : val.lower() in [ 'yes', 'no' ],                             "ENABLED has to be either 'yes' or 'no'"),
    "cname"   : ( lambda val : "." not in val  and  "/" not in val  and  "\\" not in val,  "No special characters allowed in cname"),
    "import"  : ( lambda val : "." not in val  and  "/" not in val  and  "\\" not in val,  "No special characters allowed in import class name"),
    "lang"    : ( lambda val : val in __KNOWN_LANGUAGES,                                   "lang must be one of the known languages: " + ', '.join(__KNOWN_LANGUAGES)),
    "module"  : ( lambda val : True,                                                       ""),
    "path"    : ( lambda val : True,                                                       ""),
}

def __get_component_dir():
    return settings.get_root_dir() + settings.CONF_LOCATION + "components/"

def __read_component_manifest(fname):
    """
    Read a component config from the specified file.

    Performs some very basic sanity check.

    Return the config data as dictionary.

    """
    full_fname = __get_component_dir() + fname
    config = dict()
    f = open(full_fname, "r")
    for line in f.readlines():
        line = line.split("#", 1)[0].strip()  # Remove spaces and any comment
        if not line:
            continue
        elems = line.split("=", 1)
        token = elems[0].strip()
        if token not in __KNOWN_CONFIG_TOKENS:
            raise Exception("Unknown configuration token '%s' in file '%s'" % (token, full_fname))
        if len(elems) > 1:
            value = elems[1].strip()
        else:
            raise Exception("Configuration token '%s' in file '%s' needs to have a valye specified" % (token, full_fname))
        val_func, err_msg = __KNOWN_CONFIG_TOKENS.get(token)
        if not val_func(value):
            raise Exception("Value error for configuration token '%s' in file '%s': %s" % (token, full_fname, err_msg))
        config[token] = value
    f.close()
    return config

def __read_components_configs():
    """
    Return list of config dictionaries for all currently enabled components.

    """
    comp_manifest_files = [ name for name in os.listdir(__get_component_dir()) if name.endswith(__MANIFEST_EXTENSION) ]
    all_configs         = list()
    for fname in comp_manifest_files:
        config = __read_component_manifest(fname)
        if config['ENABLED'].lower() == 'yes':
            all_configs.append(config)
    return all_configs

def __get_class( kls ):
    """
    Return a class object for a class specified by name.

    This function is courtesy of hasen j, who supplied it as an
    answer to this StackOverflow question:

        http://stackoverflow.com/questions/452969/does-python-have-an-equivalent-to-java-class-forname

    """
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__( module )
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m

def import_all():
    """
    Import all the components for which we find manifest files.

    Components are returned in a list of tuples: For each component
    we have the class object as well as the manifest dictionary.

    """
    global __IMPORT_COMPLETE
    if not __IMPORT_COMPLETE:
        configs = __read_components_configs()
        comp_classes = list()
        for conf in configs:
            # The 'import' parameter is optional and is only used 
            # if the cname is not the name of the class we are importing.
            classname = conf['module']+"."+conf.get('import', conf['cname'])
            comp_classes.append((__get_class(classname), conf))

        __IMPORT_COMPLETE = True
        return comp_classes
    else:
        return None

