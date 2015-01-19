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


import restxclient.api as restxapi
import sys

#server    = restxapi.RestxServer("http://localhost:8080/restx")   # For testing behind proxy
server    = restxapi.RestxServer("http://localhost:8001")         # For direct connection

print server.get_all_component_names_plus(False)


component = server.get_component("DatabaseAccess")
print component.get_all_services()

print "\n\nAll services...\n\n"

for sname, sdef in component.get_all_services().items():
    print "@@@@ sname = ", sdef

print "\n\nOne service...\n\n"

srv = component.get_service("entries")
print "@@@@ src: ", srv

print "\n\nPositional parameters...\n\n"

print srv.get_positional_param_names()

print "\n\n-------------------------------------------\n\n"

print "\n\nAll resource names...\n\n"

print server.get_all_resource_names()


print "\n\nAll resource names PLUS...\n\n"


print server.get_all_resource_names_plus()


print "\n\nOne resource...\n\n"

r = server.get_resource("MyJavaTestComponent")
print r

print "\n\n--------------------------------------------\n\n"



component          = server.get_component("TwitterComponent")
rt                 = component.get_resource_template()
rt.params          = dict(account_name="BrendelConsult", account_password="foobar")
rt.description     = "Some description"
rt.suggested_name  = "SomeName"
resource           = rt.create_resource()
sys.exit(1)














rt = component.get_resource_template()
rt.params         = dict(db_connection_string="/home/jbrendel/Programming/MuleSoft/RESTx/test_db", id_column="ID", table_name="Person")
rt.description    = "Some description"
rt.suggested_name = "somename_p"

component = rt.create_specialized_component()
print component

component = server.get_component("somename_p", specialized=True)
print component

rt = component.get_resource_template()
rt.suggested_name = "somename_p_final"
rt.params = dict(db_connection_string="foo")
c2 = rt.create_resource()


print c2.get_all_services()
s = c2.get_service("entries")
print s

print s.access()
"""


print "\n\n--------------------------------------------\n\n"

#status, data = server.get_resource("MyGoogleSearch").get_service("search").set("query", "mulesoft").access()

#print data

#r.delete()
"""


 
