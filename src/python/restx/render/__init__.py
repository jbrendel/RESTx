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
This module provides renderers for data into
different output formats.

You can import these classes straight from module level:

    * BaseRenderer

"""
# Export classes on module level, so that users don't need
# to specify the individual file names in their imports.
from restx.render.htmlrenderer     import HtmlRenderer
from restx.render.jsonrenderer     import JsonRenderer
from restx.render.extjsonrenderer  import ExtJsonRenderer
from restx.render.wwwformrenderer  import WwwFormRenderer
from restx.render.textrenderer     import TextRenderer
from restx.render.xmlrenderer      import XmlRenderer
from restx.render.csvrenderer      import CsvRenderer

# Add new renderers here...
KNOWN_RENDERERS = {
    ""                                   : HtmlRenderer,
    "*/*"                                : HtmlRenderer,
    "text/html"                          : HtmlRenderer,
    "text/csv"                           : CsvRenderer,
    "text/plain"                         : TextRenderer,
    "application/json"                   : JsonRenderer,
    "application/xml"                    : XmlRenderer,
    "application/ext+json"               : ExtJsonRenderer,
    "application/x-www-form-urlencoded"  : WwwFormRenderer,
}

# Some clients cannot properly deal with the content type
# headers. Therefore, we allow an additional mechanism:
# Specify the content type you send or want as a .xyz
# behind the service method name (sub-resource) in the URI.
# If 'xyz' is one of the recognized ones below, the content
# type (or accept header) is assumed to be of whatever we
# translate it to below.
RENDERER_ID_SHORTCUTS = {
    "csv"      : "text/csv",
    "xml"      : "application/xml",
    "json"     : "application/json",
    "ext_json" : "application/ext+json",
}

DEFAULT_OUTPUT_TYPES          = [ "application/json", "application/xml", "text/html", "*/*" ]
DEFAULT_INPUT_TYPES           = [ "application/json", "application/x-www-form-urlencoded" ]

KNOWN_INPUT_RENDERERS  = dict( [ (type_str, KNOWN_RENDERERS[type_str]) for type_str in KNOWN_RENDERERS.keys() if KNOWN_RENDERERS[type_str]().canParse() ] )
KNOWN_OUTPUT_RENDERERS = dict( [ (type_str, KNOWN_RENDERERS[type_str]) for type_str in KNOWN_RENDERERS.keys() if KNOWN_RENDERERS[type_str]().canRender() ] )


