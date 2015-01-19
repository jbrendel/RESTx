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
 * A sample template for RESTx components, written in Java.
 */

package ___MODULE_NAME_PLACEHOLDER___;

import java.math.BigDecimal;                        // Default type for numeric values

import org.mulesoft.restx.component.BaseComponent;  // Base class for all components
import org.mulesoft.restx.component.api.*;          // Imports all aspects of the API
import org.mulesoft.restx.exception.*;              // Imports RESTx exceptions, which you can throw or handle

// -----------------------------------------------
// Tell RESTx some information about this component.
// -----------------------------------------------
@ComponentInfo(name = "SampleComponent",
               desc = "One line description of the component",
               doc  = "Longer description text, possibly multi-line, goes here")
public class SampleComponent extends BaseComponent
{    
    // ---------------------------------
    // Resource creation time parameters
    // ---------------------------------
    // Currently, only the following types are supported for parameters:
    // String, Boolean, Number

    @Parameter(name="someParameter", desc="Short description of this parameter")
    public String someParameter;    // without default: parameter is mandatory
    
    @Parameter(name="anotherParameter", desc="Short description of this parameter")
    @Default("123.4")               // default value (as string representation) is specified: parameter is optional
    public BigDecimal anotherParameter;

                                    // Use 'Boolean' as type for boolean parameters.
    
    // ---------------
    // Service methods
    // ---------------
    @Service(desc = "This is the XYZ subresource service")
    @ParamsInReqBody                                                   // Optional: Allows parameters to be sent in the request body.
    //@InputType(InputType.NO_INPUT)                                   // Optional: Specify supported input content types, use @InputTypes({...}) for multiple
    @OutputTypes({"application/json", "text/html"})                    // Optional: Specify supported output content types, use @OutputType() for single
    public Result someSubresource(HttpMethod method, Object input,     // These two parameters are always present
                         
                                  // Here now the parameters that are exposed on the URI command line

                                  // The following defines a non-positional, mandatory parameter
                                  @Parameter(name="text", desc="This is a text parameter")
                                  String     text,
                                 
                                  // This defines an optional, positional parameter. Note that positional
                                  // parameters may either be set with query-type arguments on the URI
                                  // command line, or as path elements in the URI.
                                  @Parameter(name="num", desc="A numeric parameter", positional=true)
                                  @Default("10")
                                  BigDecimal num)
    {
        // -------------------------------------------------
        // Any kind of processing may take place here.
        // No restriction on the available language features
        // and accessible libraries.
        
        // -----------------------------------------------
        // BaseComponent provides a few facilities to make
        // life easier for the component author.
        //
        // Specifically:
        //
        // HTTP access:
        //     httpGet()
        //     httpPost()
        //     setCredentials()
        //
        // Storage:
        //     getFileStorage() (providing: loadFile(), storeFile(), deleteFile(), listFiles())
        //
        // Accessing other resources:
        //     accessResource()
        //     makeResource()
        //
        // Processing JSON:
        //     fromJson()
        //     toJson()

        // -------------------------------------------------------------------------
        // Preparing return data:
        //     Result object, with convenient factory methods.
        //
        // Return data can be objects of the following types: String, Boolean,
        // Number, HashMap or ArrayList. HashMaps or ArrayLists may contain elements
        // of any of these types, including further HashMaps or ArrayLists. Thus,
        // it is possible to assemble lists or complex, hiearchical data structures
        // as return values.

        String data = "Some return value";

        return Result.ok(data);
    }
}


