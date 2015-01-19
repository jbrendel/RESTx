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
A sample template for RESTx components, written in Python.

"""
import urllib

import restx.components
import restx.settings as settings

from   restx.platform_specifics     import STORAGE_OBJECT
from   restx.components.api         import *
from   org.mulesoft.restx.exception import *

class _ResourceCreateForm(BaseComponent):
    # Name, description and doc string of the component as it should appear to the user.
    NAME             = "_ResourceCreateForm"    # Names starting with a '_' are kept private
    DESCRIPTION      = "Allows creation of a new resource by displaying a resource creation form"
    DOCUMENTATION    = \
"""The resource gets the name of a component as parameter at run time.
It then reads information about the component and constructs a proper
HTML form suitable for resource creation.

The user submits the filled-out form and a new resource is created.
"""

    PARAM_DEFINITION = {}
    
    # A dictionary with information about each exposed service method (sub-resource).
    SERVICES         = {
                           "form" : {
                               "desc" : "Show the resource creation form",
                               "params" : {
                                   "component_name" : ParameterDef(PARAM_STRING, "Name of the component", required=True),
                                   "message"        : ParameterDef(PARAM_STRING, "An error message", required=False, default=""),
                                   "specialized"    : ParameterDef(PARAM_BOOL,   "Indicates if this is based on a specialized component", required=False, default=False),
                               },
                               "positional_params": [ "component_name" ]
                            },
                       }
    
    def __create(self, input, component_name, specialized=False):
        """
        Accept a resource creation form for a specified component.

        """
        d = dict()
        for name, value in input.items():
            path_elems = name.split("__")
            d2 = d
            for i, pe in enumerate(path_elems):
                if i < len(path_elems)-1:
                    # More elements to come later? We must create a dict
                    d2 = d2.setdefault(pe, dict())
                else:
                    if value:
                        d2[pe] = value

        try:
            return (True, makeResource(component_name, d, specialized), d)
        except RestxException, e:
            return (False, e.msg, d)
        
    def form(self, method, input, component_name, message="", specialized=False):
        """
        Display a resource creation form for a specified component.
        
        @param method:          The HTTP request method.
        @type method:           string
        
        @param input:           Any data that came in the body of the request.
        @type input:            string

        @param component_name:  Name of the component for which to create the resource.
        @type component_name:   string

        @param message:         An error message to be displayed above the form.
        @type message:          string

        @return:                The output data of this service.
        @rtype:                 Result

        """
        input_params = dict()
        input_rctp   = dict()
        if input  and  HttpMethod.POST:
            flag, msg, input = self.__create(input, component_name, specialized)
            if not flag:
                message = msg
            else:
                return Result.created(msg['uri'], msg)

        if input:
            if type(input) is dict:
                # We receive a dict of values if the 'create' method discovered an
                # error. In that case, the values should be used to pre-populate
                # the fields when the form is re-displayed (with the error messsage
                # on top).
                input_rctp   = input.get('resource_creation_params', dict())   # Resource creation time parameters
                input_params = input.get('params', dict())                     # Other parameters

        if specialized:
            # Need to read the definition of the partial resource and get the
            # component name from there.
            specialized_code_name = component_name
            specialized_def       = STORAGE_OBJECT.loadResourceFromStorage(specialized_code_name, True)
            component_uri         = specialized_def['private']['code_uri']
            elems                 = component_uri.split("/")
            component_name        = elems[len(elems)-1]

        # Take the parameter map from the component
        comp = restx.components.make_component(component_name)
        if not comp:
            return Result.notFound("Cannot find component '%s'" % component_name)
        header = settings.HTML_HEADER

        # Assemble the form elements for the parameters
        params = dict()
        params.update(comp.getParams())  # In case this is a Java component, we get a Python dict this way

        if specialized:
            fname = specialized_def['public']['name']
            fdesc = specialized_def['public']['desc']
            # Remove all parameters that have been specified in the specialized component resource
            # definition already
            spec_params = specialized_def['private'].get('params')
            if spec_params:
                for name in spec_params:
                    if name in params:
                        del params[name]
        else:
            fname = comp.getName()
            fdesc = comp.getDesc()

        param_fields_html = ""
        if params:
            param_field_names = params.keys()
            param_field_names.sort()
            for pname in param_field_names:
                pdef = params[pname]
                if not pdef.required:
                    opt_str = "<br>optional, default: %s" % pdef.getDefaultVal()
                else:
                    opt_str = ""
                values = input_params.get(pname)
                if type(values) is not list  and  pdef.isList():
                    if values is None:
                        values = []
                    else:
                        values = [ values ]
                param_fields_html += \
"""<tr>
    <td valign=top id="%s_name">%s<br><small>(%s%s)</small></td>
    <td valign=top>%s</td>
</tr>""" % (pname, pname, pdef.desc, opt_str, pdef.html_type("params__"+pname, values))

        if message:
            msg = "<b><i><font color=red>%s</font></i></b><br><p>" % message
        else:
            msg = ""

        body = """
<h3>Resource creation form for: %s</h3>
<p><i>"%s"</i></p>

<hr>
Please enter the resource configuration...<br><p>
%s
<form id="resource_form" name="input" action="%s" method="POST">
    <table>""" % (fname, fdesc, msg, "%s%s/form/%s%s" % (settings.DOCUMENT_ROOT, self.getMyResourceUri(),
                                                           component_name if not specialized else specialized_code_name, "?specialized=y" if specialized else ""))
        # Gather any initial values of the resource creation time form fields
        suggested_name_value = input_rctp.get("suggested_name", "")
        if suggested_name_value:
            suggested_name_value = 'value="%s" ' % suggested_name_value
        desc_value           = input_rctp.get("desc", "")
        if desc_value:
            desc_value = 'value="%s" ' % desc_value
        specialized_value    = "checked " if input_rctp.get("specialized") in [ "on", "ON" ] else " "
        if not specialized:
            body += """
        <tr>
            <td id="Make_this_a_specialized_component_name">Make this a specialized component:</td>
            <td><input type="checkbox" %s id="resource_creation_params__specialized" name="resource_creation_params__specialized" /><label for=resource_creation_params__specialized><small>Can only be used as basis for other resources</small></label></td>
        </tr>
            """ % specialized_value
        body += """
        <tr>
            <td id="Resource_name_name">Resource name:</td>
            <td><input type="text" %sname="resource_creation_params__suggested_name" id="resource_creation_params__suggested_name" /></td>
        </tr>
        <tr>
            <td id="Description_name">Description:<br><small>(optional)</small></td>
            <td><input type="text" %sname="resource_creation_params__desc" id="resource_creation_params__desc" /></td>
        </tr>
        %s
        <tr><td colspan=2 align=center><input id="submit_button" type="submit" value="Submit" /></tr>
    </table>
</form>""" % (suggested_name_value, desc_value, param_fields_html)

        footer = settings.HTML_FOOTER

        return Result.ok(header + body + footer).addHeader("Content-type", "text/html; charset=UTF-8")

