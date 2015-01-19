/*      
 *  RESTx: Sane, simple and effective data publishing and integration. 
 *  
 *  Copyright (C) 2010   MuleSoft Inc.    http://www.mulesoft.com 
 *  
 *  This program is free software: you can redistribute it and/or modify 
 *  it under the terms of the GNU General Public License as published by 
 *  the Free Software Foundation, either version 3 of the License, or 
 *  (at your option) any later version. 
 * 
 *  This program is distributed in the hope that it will be useful, 
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of 
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
 *  GNU General Public License for more details. 
 * 
 *  You should have received a copy of the GNU General Public License 
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>. 
 */ 

 
/*
 * A sample component that interacts with Twitter, written in Javascript.
 */

/*
 * Component Meta Information
 */
this.name = "JsTwitterComponent"

this.description = "Provides access to a Twitter account."

this.documentation = "The Twitter component is designed to provide access to a Twitter account.\n"
                   + "It can be used to get as well as update status, or to view the timeline of a Twitter account.\n"
                   + "To create the resource, the Twitter account name and password need to be specified."

this.parameters = {
  accountName     : { type: TYPE.STRING, description: "Twitter account name" },
  accountNumber   : { type: TYPE.NUMBER, description: "Twitter account name" },
  accountPassword : { type: TYPE.PASSWORD, description: "Password" }
}

/*
 * User status Service
 */
status.description = "You can GET the status or POST a new status to it."
status.inputType   = "text/plain"
status.outputType  = "text/plain"

function status(method, input) {
  
  function getStatus() {
    result = RESTx.httpGet("http://api.twitter.com/1/users/show.json?screen_name=" + accountName)
    
    return response(function() { return RESTx.fromJson(result.data).get("status").get("text") })
  }
  
  function postStatus(input) {
    RESTx.httpSetCredentials(accountName, accountPassword)
    result = RESTx.httpPost("http://api.twitter.com/1/statuses/update.json", "status="+ input)
    
    return response(function() { return "Status updated" })
  }
  
  switch(method) {
    case HTTP.GET : return getStatus()
    case HTTP.POST: return postStatus(input)
    default       : return RESULT.methodNotAllowed(method)
  }
}

/*
 * User timeline Service
 */
timeline.description = "You can GET the timeline of the user."
timeline.inputTypes  = []
timeline.parameters  = {
  count  : { type: TYPE.NUMBER, description: "Number of results", defaultValue: 20},
  filter : { type: TYPE.BOOLEAN, description: "If set, only 'important' fields are returned", defaultValue: true}
}

function timeline(method, input, count, filter) {
  
  function filterResults(jsonResults) {
    filteredResults = []
    
    for (i=0; i<jsonResults.size(); i++) {
      jsonResult = jsonResults.get(i)
      id = jsonResult.get("id")

      user = jsonResult.get("user")
      screenName = user.get("screen_name")
      
      filteredResult = {
	user   : {screen_name: screenName,
		  name: user.get("name"),
		  followers: user.get("followers_count")},
	message: {id: id,
		  date: jsonResult.get("created_at"),
		  text: jsonResult.get("text"),
		  reply: "http://twitter.com/?status=@"+screenName+"&in_reply_to_status_id="+id+"&in_reply_to="+screenName}
	}
      
      filteredResults[filteredResults.length] = filteredResult
    }
    
    return filteredResults
  }
  
  if (method != HTTP.GET) return RESULT.methodNotAllowed(method)

  RESTx.httpSetCredentials(accountName, accountPassword)
  result = RESTx.httpGet("http://api.twitter.com/1/statuses/user_timeline.json?count=" + count)

  return response(function() {
                    jsonResults = RESTx.fromJson(result.data)
                    return filter ? filterResults(jsonResults) : jsonResults
                  })
}

/*
 * Supporting functions
 */
function response(successFunction) {
  return result.status == HTTP.OK ? RESULT.ok(successFunction())
                                  : RESULT.internalServerError("Problem with Twitter: " + result.status + " " + result.data)
}
