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

from restx.components.api import *

class DownloadAnalysis(BaseComponent):

    # Name, description and doc string of the component as it should appear to the user.
    NAME             = "DownloadAnalysis"
    DESCRIPTION      = "Sub resources to analyse downloads"
    DOCUMENTATION    = "Interesting information obtained when correlating access and download logs"

    PARAM_DEFINITION = {
                           "access_log_resource" :    ParameterDef(PARAM_STRING, "Resource URI for the access log", required=True),
                           "download_log_resource" :  ParameterDef(PARAM_STRING, "Resource URI for the download log", required=True),
                       }
    
    SERVICES         = {
                           "referrers" : {
                               "desc" : "Show the referrers that lead to downloads",
                           }
                       }
        

    def referrers(self, method, input):
        status, access_log   = accessResource(self.access_log_resource)
        status, download_log = accessResource(self.download_log_resource)
        # Get all IP addresses from which we downloaded
        download_ips = dict([ (e.split(" ", 1)[0], e.split(" ", 1)[1].split()[2][1:]) for e in download_log ] )
        result = list()
        for line in access_log:
            elems = line.split('"')
            ip_date = elems[0].split(" ",1)
            ip = ip_date[0]
            dt = ip_date[1].split()[2][1:]
            if ip in download_ips:
                result.append(dict(firstcontact_time=dt, download_time=download_ips[ip], ipaddr=ip,
                                   trace="%s/subset?filter=%s&unique_only=f" % (self.access_log_resource, ip), referrer=elems[3]))

        return Result.ok(result)

