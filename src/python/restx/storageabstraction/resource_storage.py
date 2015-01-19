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
Base class from which all storage abstractions derive.

"""
import restxjson as json

# RESTx imports
from restx.storageabstraction.file_storage import FileStorage
from org.mulesoft.restx.exception        import *

RESOURCE_EXTENSION         = ".rxr"
PARTIAL_RESOURCE_EXTENSION = ".prxr"

class ResourceStorage(FileStorage):
    """
    Implementation of resource storage methods.

    """

    def loadResourceFromStorage(self, resource_name, is_partial=False):
        """
        Load the specified resource from storage.

        @param resource_name:    Name of the selected resource.
        @type resource_name:     string

        @param is_partial:       Indicates whether we are loading a parrral resource.
        @type is_partial:        boolean

        @return                  A Python dictionary representation or None
                                 if not found.
        @rtype                   dict

        """
        try:
            buf = self.loadFile(resource_name + (PARTIAL_RESOURCE_EXTENSION if is_partial else RESOURCE_EXTENSION))
        except RestxFileNotFoundException, e:
            return None
        obj = json.loads(buf)
        if "extends" in obj:
            base_obj = self.loadResourceFromStorage(obj["extends"], is_partial=True)  # Base resources can only be partial
            try:
                # Merge any parameters that are defined in the base resource into the output dictionary.
                for key, val in base_obj['private']['params'].items():
                    if key not in obj:
                        obj['private']['params'][key] = val
                obj['private']['code_uri'] = base_obj['private']['code_uri']
            except:
                return None
        return obj

    def deleteResourceFromStorage(self, resource_name, is_partial=False):
        """
        Delete the specified resource from storage.

        @param resource_name:    Name of the selected resource.
        @type resource_name:     string

        @param is_partial:       Indicates whether we are loading a parrral resource.
        @type is_partial:        boolean

        """
        self.deleteFile(resource_name + (PARTIAL_RESOURCE_EXTENSION if is_partial else RESOURCE_EXTENSION))

    def listResourcesInStorage(self, partials=False):
        """
        Return list of resources which we currently have in storage.

        @param partials:       Indicates whether we are looking for partial resources.
        @type partials:        boolean

        @return:               List of resource names.
        @rtype:                list

        """
        if partials:
            extension = PARTIAL_RESOURCE_EXTENSION
        else:
            extension = RESOURCE_EXTENSION
        try:
            dir_list = [ name[:-len(extension)] for name in self.listFiles(extension) ]
            return dir_list
        except Exception, e:
            raise RestxException("Problems getting resource list from storage: " + str(e))

    def writeResourceToStorage(self, resource_name, resource_def, is_specialized=False):
        """
        Store a resource definition.
        
        No return value, but raises RestxException if there is an issue.
        
        @param resource_name:  The storage name for this resource
        @type  resource_name:  string
        
        @param resource_def:   The dictionary containing the resource definition.
        @type  resource_def:   dict

        @param is_specialized: Flag indicates whether a specialized component resource should
                               be created. Those can only serve as base for other resources
                               and also carry a different file extension.
        @type  is_specialized: boolean
        
        @raise RestxException: If the resource cannot be stored.
            
        """
        if is_specialized:
            extension = PARTIAL_RESOURCE_EXTENSION
        else:
            extension = RESOURCE_EXTENSION
        try:
            buf = json.dumps(resource_def, indent=4)
            self.storeFile(resource_name + extension, buf)
        except Exception, e:
            raise RestxException("Problems storing new resource: " + str(e))

