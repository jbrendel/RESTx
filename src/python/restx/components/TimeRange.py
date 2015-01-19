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

# Imports all aspects of the API
from restx.components.api import *

from datetime import datetime, timedelta

# -------------------------------------------------------
# A RESTx component needs to be derived from BaseComponent.
# -------------------------------------------------------
class TimeRange(BaseComponent):

    # Name, description and doc string of the component as it should appear to the user.
    NAME             = "TimeRange"
    DESCRIPTION      = "Allows the selection of time ranges to be sent to other resources."
    DOCUMENTATION    = "Longer description text possibly multiple lines."

    PARAM_DEFINITION = {
                           "base_resource"   :  ParameterDef(PARAM_STRING, "The URI of the resource that accepts time ranges", required=True),
                           "start_time_name" :  ParameterDef(PARAM_STRING, "Name of the parameter for the base resource, which sets the start time",
                                                             required=False, default="start_time"),
                           "end_time_name"   :  ParameterDef(PARAM_STRING, "Name of the parameter for the base resource, which sets the end time",
                                                             required=False, default="end_time"),
                           "count_flag_name" :  ParameterDef(PARAM_STRING, "Name of the flag to get only a log line count",
                                                             required=False, default="count_only"),
                           "filter_name"     :  ParameterDef(PARAM_STRING, "Name of the parameter to specify a filter",
                                                             required=False, default="filter"),
                           "unique_only_name":  ParameterDef(PARAM_STRING, "Name of the parameter to specify whether we only want unique entries.",
                                                             required=False, default="unique_only"),
                       }
    
    # A dictionary with information about each exposed service method (sub-resource).
    SERVICES         = {
                           # Key into the dictionary is the service name. Has to be an
                           # exact function name.
                           "current_time" : {
                               "desc" : "The current time representation",
                           },
                           "today" : {
                               "desc" : "Today's entries",
                               "params" : {
                                   "count_only" :  ParameterDef(PARAM_BOOL,   "If set then we only get the count of lines, not the lines themselves.", required=False, default=False), 
                                   "filter" :      ParameterDef(PARAM_STRING, "Specify one or more filter expressions, separated by ';'. Specify exclusions by pre-pending a '-'. For example: 'foo;-bar;blah' means that 'foo' and 'bar' need to be in the line, but 'bar' must not be present.",
                                                                required=False, default=""), 
                                   "unique_only" : ParameterDef(PARAM_BOOL,   "If set then we only consider the first appearance of an IP address.", required=False, default=True),

                                }
                           },
                           "yesterday" : {
                               "desc" : "Yesterday's entries",
                               "params" : {
                                   "count_only" :  ParameterDef(PARAM_BOOL, "If set then we only get the count of lines, not the lines themselves.", required=False, default=False), 
                                   "filter" :      ParameterDef(PARAM_STRING, "Specify one or more filter expressions, separated by ';'. Specify exclusions by pre-pending a '-'. For example: 'foo;-bar;blah' means that 'foo' and 'bar' need to be in the line, but 'bar' must not be present.",
                                                                required=False, default=""), 
                                   "unique_only" : ParameterDef(PARAM_BOOL,   "If set then we only consider the first appearance of an IP address.", required=False, default=True),
                                }
                           },
                           "last7days" : {
                               "desc" : "Entries over the last 7 days",
                               "params" : {
                                   "count_only" :  ParameterDef(PARAM_BOOL, "If set then we only get the count of lines, not the lines themselves.", required=False, default=False), 
                                   "filter" :      ParameterDef(PARAM_STRING, "Specify one or more filter expressions, separated by ';'. Specify exclusions by pre-pending a '-'. For example: 'foo;-bar;blah' means that 'foo' and 'bar' need to be in the line, but 'bar' must not be present.",
                                                                required=False, default=""), 
                                   "unique_only" : ParameterDef(PARAM_BOOL,   "If set then we only consider the first appearance of an IP address.", required=False, default=True),
                                }
                           },
                           "last30days" : {
                               "desc" : "Entries over the last 30 days",
                               "params" : {
                                   "count_only" :  ParameterDef(PARAM_BOOL, "If set then we only get the count of lines, not the lines themselves.", required=False, default=False), 
                                   "filter" :      ParameterDef(PARAM_STRING, "Specify one or more filter expressions, separated by ';'. Specify exclusions by pre-pending a '-'. For example: 'foo;-bar;blah' means that 'foo' and 'bar' need to be in the line, but 'bar' must not be present.",
                                                                required=False, default=""), 
                                   "unique_only" : ParameterDef(PARAM_BOOL,   "If set then we only consider the first appearance of an IP address.", required=False, default=True),
                                }
                           },
                           "last90days" : {
                               "desc" : "Entries over the last 90 days",
                               "params" : {
                                   "count_only" :  ParameterDef(PARAM_BOOL, "If set then we only get the count of lines, not the lines themselves.", required=False, default=False), 
                                   "filter" :      ParameterDef(PARAM_STRING, "Specify one or more filter expressions, separated by ';'. Specify exclusions by pre-pending a '-'. For example: 'foo;-bar;blah' means that 'foo' and 'bar' need to be in the line, but 'bar' must not be present.",
                                                                required=False, default=""), 
                                   "unique_only" : ParameterDef(PARAM_BOOL,   "If set then we only consider the first appearance of an IP address.", required=False, default=True),
                                }
                           },
                       }

    def __make_time_str(self, dt):
        return dt.strftime("%d/%b/%Y:%H:%M:%S")

    def __make_params(self, start, end, count_only, filter, unique_only):
        p = dict()
        p[self.start_time_name] = self.__make_time_str(start)
        p[self.end_time_name]   = self.__make_time_str(end)
        if self.count_flag_name:
            p[self.count_flag_name] = count_only
        if self.filter_name:
            p[self.filter_name] = filter
        if self.unique_only_name:
            p[self.unique_only_name] = unique_only
        return p

    def current_time(self, method, input):
        """
        Return the current time.

        """
        return Result.ok(self.__make_time_str(datetime.now()))

    def today(self, method, input, count_only, filter, unique_only):
        now   = datetime.now()
        start = datetime(now.year, now.month, now.day, 0, 0, 0)
        status, data = accessResource(self.base_resource, params=self.__make_params(start, now, count_only, filter, unique_only))
        return Result(status, data)

    def yesterday(self, method, input, count_only, filter, unique_only):
        ld    = datetime.now()-timedelta(1)
        start = datetime(ld.year, ld.month, ld.day)
        end   = start+timedelta(1)
        status, data = accessResource(self.base_resource, params=self.__make_params(start, end, count_only, filter, unique_only))
        return Result(status, data)

    def last7days(self, method, input, count_only, filter, unique_only):
        now   = datetime.now()
        start = now-timedelta(7)
        status, data = accessResource(self.base_resource, params=self.__make_params(start, now, count_only, filter, unique_only))
        return Result(status, data)

    def last30days(self, method, input, count_only, filter, unique_only):
        now   = datetime.now()
        start = now-timedelta(30)
        status, data = accessResource(self.base_resource, params=self.__make_params(start, now, count_only, filter, unique_only))
        return Result(status, data)

    def last90days(self, method, input, count_only, filter, unique_only):
        now   = datetime.now()
        start = now-timedelta(90)
        status, data = accessResource(self.base_resource, params=self.__make_params(start, now, count_only, filter, unique_only))
        return Result(status, data)

       

