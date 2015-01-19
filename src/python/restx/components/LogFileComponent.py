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
# Imports all aspects of the API
from restx.components.api import *

import os, sys
import re

from stat     import *
from datetime import date, datetime, timedelta

MONTH_LOOKUP = {
    "Jan" : "01",
    "Feb" : "02",
    "Mar" : "03",
    "Apr" : "04",
    "May" : "05",
    "Jun" : "06",
    "Jul" : "07",
    "Aug" : "08",
    "Sep" : "09",
    "Oct" : "10",
    "Nov" : "11",
    "Dec" : "12",
}


def makedatestr(date_text):
    """
    date_text has to be in format DD/mmm/YYYY/HH:MM[:SS]

    Return string "YYYYMMDD:HH:MM[:SS]

    If it can't be parsed properly then it just returns
    an empty string.

    """
    try:
        _date, _time =  date_text.split(":", 1)
        day, month, year = _date.split("/")
        linedate = year + MONTH_LOOKUP[month] + day + ":" + _time
    except Exception, e:
        linedate = ''

    return linedate

class SignalException(Exception):
    pass

# Function to read lines from file and extract the date and time
def getdata(handle, bufsize):
    """Read a line from a file

    Return a tuple containing:
        the date/time in a format such as 'Jan 15 20:14:01'
        the line itself

    The last colon and seconds are optional and
    not handled specially

    """
    try:
        line = handle.readline(bufsize)
    except Exception, e:
        raise RestxException("File I/O Error: " + str(e))
    if line == '':
        raise SignalException()
    if line[-1] == '\n':
        line = line.rstrip('\n')
    else:
        if len(line) >= bufsize:
            raise RestxException("Line length exceeds buffer size")
        else:
            raise RestxException("Missing newline")
        exit(1)
    words = line.split(' ')
    if len(words) >= 6:
        tword = words[3][1:]
        linedate = makedatestr(tword)
    else:
        linedate = ''

    """
    if len(words) >= 3:
        linedate = words[0] + " " + words[1] + " " + words[2]
    else:
        linedate = ''
    """
    return (linedate, line)


class LogFileComponent(BaseComponent):

    # Name, description and doc string of the component as it should appear to the user.
    NAME             = "LogFileComponent"
    DESCRIPTION      = "Extracts lines from a web server log file"
    DOCUMENTATION    = "A longer description"

    PARAM_DEFINITION = {
                           "filename"  :      ParameterDef(PARAM_STRING, "Full file name of the logfile", required=True), 
                           "mustContain" :    ParameterDef(PARAM_STRING, "Filter terms a line must contain, separate multiples with ';'", required=False, default=""),
                           "mustNotContain" : ParameterDef(PARAM_STRING, "Filter terms a line must NOT contain, separate multiples with ';'", required=False, default=""),
                       }
    
    # A dictionary with information about each exposed service method (sub-resource).
    SERVICES         = {
                          "subset" : {
                               "desc" : "Accesses a region of lines from the logfile, based on start and end time. " + \
                                        "If no times are provided then it just takes the last 24 hours.",
                               "params" : {
                                   "filter"      :  ParameterDef(PARAM_STRING, "Filter terms, separated by ';'. Prepend a '-' for exclusion.", required=False, default=""), 
                                   "start_time"  :  ParameterDef(PARAM_STRING, "Start of time/date range. Format: DD/mmm/YYYY:HH:MM[:SS]", required=False, default=""), 
                                   "end_time"    :  ParameterDef(PARAM_STRING, "End of time/date range.   Format: DD/mmm/YYYY:HH:MM[:SS]", required=False, default=""), 
                                   "count_only"  :  ParameterDef(PARAM_BOOL,   "If set then we only get the count of lines, not the lines themselves.", required=False, default=False), 
                                   "unique_only" :  ParameterDef(PARAM_BOOL,   "If set then we only consider the first appearance of an IP address.", required=False, default=True), 
                               },
                           },
                       }
        

    def subset(self, method, input, filter, start_time, end_time, count_only, unique_only):
        """
        The method that implements log search
        
        """
        # Sanity checking of the parameters
        p = re.compile(r'^([0-3][0-9])/[a-zA-Z]{3}/[1-2][0-9][0-9][0-9]:([2][0-3]|[0-1][0-9]):[0-5][0-9](:[0-5][0-9])?$')
        if start_time  and  not p.match(start_time):
            raise RestxBadRequestException("Invalid start time specification")
        if end_time  and  not p.match(end_time):
            raise RestxBadRequestException("Invalid end time specification")
	
        # Setting default start and end time if one or both of those values are missing
        now = datetime.now()
        if end_time and not start_time:
            # Everything from the beginning to the specified end time
            start_time = "01/Jan/1900:00:00:00"
        elif start_time and not end_time:
            # Everything from the specified start to the end
            end_time = now.strftime("%d/%b/%Y:%H:%M:%S")
        elif not start_time and not end_time:
            # No times? Get the last 24 hours
            start_time = (now-timedelta(1)).strftime("%d/%b/%Y:%H:%M:%S")
            end_time   = now.strftime("%d/%b/%Y:%H:%M:%S")

        searchstart = makedatestr(start_time)
        searchend   = makedatestr(end_time)

        try:
            handle = open(self.filename,'r')
        except:
            raise RestxException("File Open Error")

        # Set some initial values
        bufsize = 4096  # handle long lines, but put a limit them
        rewind  =  100  # arbitrary, the optimal value is highly dependent on the structure of the file
        limit   =   75  # arbitrary, allow for a VERY large file, but stop it if it runs away
        count   =    0
        size    =    os.stat(self.filename)[ST_SIZE]
        beginrange   = 0
        midrange     = size / 2
        oldmidrange  = midrange
        endrange     = size
        linedate     = ''

        pos1 = pos2  = 0

        if count_only:
            out = 0
        else:
            out = list()
        try:
            # Seek using binary search
            while pos1 != endrange and oldmidrange != 0 and linedate != searchstart:
                handle.seek(midrange)
                linedate, line = getdata(handle, bufsize)    # sync to line ending
                pos1 = handle.tell()
                if midrange > 0:             # if not BOF, discard first read
                    linedate, line = getdata(handle, bufsize)

                pos2 = handle.tell()
                count += 1
                if  searchstart > linedate:
                    beginrange = midrange
                else:
                    endrange = midrange
                oldmidrange = midrange
                midrange = (beginrange + endrange) / 2
                if count > limit:
                    raise RestxException("ERROR: ITERATION LIMIT EXCEEDED")

            # Rewind a bit to make sure we didn't miss any
            seek = oldmidrange
            while linedate >= searchstart and seek > 0:
                if seek < rewind:
                    seek = 0
                else:
                    seek = seek - rewind
                handle.seek(seek)
                linedate, line = getdata(handle, bufsize)    # sync to line ending
                linedate, line = getdata(handle, bufsize)

            # Scan forward
            while linedate < searchstart:
                linedate, line = getdata(handle, bufsize)

            # Now that the preliminaries are out of the way, we just loop,
            # reading lines and storing them in a list (or counting) until they
            # are beyond the end of the range we want
            # However, if unique_only is set then we maintain a set, which
            # tells us whether we have an entry for this IP address already
            # and will ignore further entries.
            if unique_only:
                hitlist = set()
            do_filter = False
            inc_filters = list()
            exl_filters = list()
            if filter:
                do_filter = True
                filter_elems = filter.split(";")
                inc_filters.extend([ f for f in filter_elems if not f.startswith("-") ])
                exl_filters.extend([ f[1:] for f in filter_elems if f.startswith("-") ])
            if self.mustContain:
                do_filter = True
                inc_filters.extend(self.mustContain.split(";"))
            if self.mustNotContain:
                do_filter = True
                exl_filters.extend(self.mustNotContain.split(";"))

            while linedate <= searchend:
                old_line = unicode(line)
                linedate, line = getdata(handle, bufsize)

                # Might not have to add this line, if the IP address appeared before
                if unique_only:
                    ipaddr, remainder = old_line.split(" ", 1)
                    if ipaddr in hitlist:
                        continue

                # Check for filter expressions
                if do_filter:
                    filter_out = False
                    for f in inc_filters:
                        if f not in old_line:
                            filter_out = True
                            break
                    for f in exl_filters:
                        if f in old_line:
                            filter_out = True
                            break
                    if filter_out:
                        continue
                    
                if unique_only:
                    hitlist.add(ipaddr)
                if count_only:
                    out += 1
                else:
                    out.append(old_line)

        except SignalException, e:
            pass

        handle.close()
      
        return Result.ok(out)

