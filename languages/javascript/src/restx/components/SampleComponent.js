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
 * A sample template for RESTx components, written in JavaScript.
 */
 
// -----------------------------------------------
// Tell RESTx some information about this component.
// -----------------------------------------------
this.name = "SampleComponent"

this.description = "One line description of the component"

this.documentation = "Longer description text, possibly multi-line, goes here"

// ---------------------------------
// Resource creation time parameters
// ---------------------------------
// Currently, only the following types are supported for parameters:
// STRING, PASSWORD, BOOLEAN, NUMBER
this.parameters = {
  someParameter    : { type: TYPE.STRING, description: "Short description of this parameter", required: true },
  anotherParameter : { type: TYPE.NUMBER, description: "Short description of this parameter", required: false, defaultValue: 20 }
}

// ---------------
// Service methods
// ---------------
// Attach these attributes to the functions you want to be service methods.
someService.description = "This is the XYZ subresource service"
//someService.inputTypes  = []                          // Optional: Specify supported input content types. Use inputType for a single value.
                                                        //           Specify an empty list here to indicate that no input is allowed.
someService.outputTypes = ["text/plain", "text/html"] // Optional: Specify supported output content types. Use outputType for a single value.

// Optional: Specify query string / URL parameters
someService.parameters = {
  // Optional: add 'positional: true' to a parameter to specify it will be provided as part of the URL and not as a query string parameter
  aNum  : { type: TYPE.NUMBER, description: "This is a numeric parameter", required: false, defaultValue: 20},
  aBool : { type: TYPE.BOOLEAN, description: "This is a boolean parameter", required: false, defaultValue: true}
}

function someService(method, input,   // Parameters method and input are always present
                     aNum, aBool)  {  // Optional: if query string parameters have been defined, service function should accept them 

  // -------------------------------------------------
  // Any kind of processing may take place here.
  // No restriction on the available language features
  // and accessible libraries.

  // -----------------------------------------------
  // A few global variables are automatically bound to make 
  // life easier for the component author.
  //
  // RESTx engine:
  //
  // HTTP access:
  //     RESTx.httpGet()
  //     RESTx.httpPost()
  //     RESTx.setCredentials()
  //
  // Storage:
  //     RESTx.getFileStorage() (providing: loadFile(), storeFile(), deleteFile(), listFiles())
  //
  // Accessing other resources:
  //     RESTx.accessResource()
  //     RESTx.makeResource()
  //
  // Processing JSON:
  //     RESTx.fromJson()
  //     RESTx.toJson()
  
  // -------------------------------------------------------------------------
  // Preparing return data:
  //     RESULT.ok()
  //     RESULT.internalServerError()
  //     RESULT.methodNotAllowed()
  //     ...
  //
  // Return data can be objects of the following types: String, Boolean,
  // Number, HashMap or ArrayList. HashMaps or ArrayLists may contain elements
  // of any of these types, including further HashMaps or ArrayLists. Thus,
  // it is possible to assemble lists or complex, hiearchical data structures
  // as return values.
  
  // -------------------------------------------------------------------------
  // HTTP method constants:
  //     HTTP.GET
  //     HTTP.POST
  //     ...

  
  
  switch(method) {
    case HTTP.GET : return RESULT.ok("Received 'GET' request")
    case HTTP.POST: return RESULT.internalServerError("'POST' not yet implemented")
    default       : return RESULT.methodNotAllowed(method)
  }
}

