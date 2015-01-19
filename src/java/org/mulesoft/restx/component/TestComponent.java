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

package org.mulesoft.restx.component;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.mulesoft.restx.component.api.*;
import org.mulesoft.restx.exception.RestxException;

@ComponentInfo(name = "TestComponent",
               desc = "This is a Java test component",
               doc  = "Here is a doc string")
public class TestComponent extends BaseComponent
{
    @Parameter(name = "api_key", desc = "This is the API key")
    // @Default("foo foo foo")
    public String api_key;

    @Parameter(name = "foo_1", desc = "This is a string choice type")
    @Choices({"Foo A", "Foo B", "Foo C"})
    @Default("Foo B")
    public String foo_1;

    @Parameter(name = "foo_list", desc = "This is a string list choice type")
    @Choices({"Foo A list item", "Foo B list item", "Foo C list item"})
    @Default("Foo B list item")
    public String[] foo_list;

    @Parameter(name = "foo_2", desc = "This is a number choice type")
    @Choices({"1", "2", "3"})
    @Default("3")
    public BigDecimal foo_2;

    @Parameter(name = "bar_list", desc = "This is a numeric list choice type")
    @Choices({"11", "22", "33", "44"})
    @Default("22")
    public BigDecimal[] bar_list;

    @Service(desc = "This is the foobar service")
    @InputType(InputType.NO_INPUT)
    // @InputType(InputType.ANY_INPUT)
    //@InputTypes({"application/json", "application/x-www-form-urlencoded"})
    @OutputTypes({"application/json", "text/html", "text/plain"})
    @ParamsInReqBody
    public Result foobar(HttpMethod method,
                         Object input,
                         @Parameter(name = "query", desc = "This is the query string", positional = true) @Default("foo") String query,
                         @Parameter(name = "num", desc = "The number of results", positional = true) @Default("10") BigDecimal num)
    {
        System.out.println("----------------------------------------------------------");
        if (input != null)
        {
            //System.out.println("### input:   " + input.getClass() + " === " + input);
        }
        //System.out.println("### method:  " + method.getClass() + " === " + method);

        //System.out.println("Query parameter: " + query);
        //System.out.println("Num parameter:   " + num);

        //System.out.println("My request headers: " + getRequestHeaders());
        //System.out.println("My request header type: " + getRequestHeaders().getClass().getName());

        final Map<String, Object> res = new HashMap<String, Object>();
        res.put("foo", "This is a test");
        final Map<String, Object> sub = new HashMap<String, Object>();
        res.put("bar", sub);
        sub.put("some value", 1);
        sub.put("another value", "Some text");
        List<Object> v = new ArrayList<Object>();
        v.add("Blah");
        v.add(12345);
        sub.put("some ArrayList", v);

        v = new ArrayList<Object>();
        v.add("Some text");
        v.add(123);
        v.add(res);

        System.out.println("Foo list: " + foo_list);
        for (String x: foo_list) {
            System.out.println("  --- " + x);
        }

        System.out.println("Bar list: " + bar_list);
        for (BigDecimal x: bar_list) {
            System.out.println("  --- " + x);
        }

        return Result.ok(v);
    }

    @Service(desc = "Makes another resource")
    public Result maker(HttpMethod method, String input) throws RestxException
    {
        final Map<String, String> params = new HashMap<String, String>();
        params.put("api_key", "123123");
        params.put("default_search", "java");

        final MakeResourceResult res = makeResource("GoogleSearchComponent", "NewResourceName",
            "Description for my resource", false, params);
        final String resbuf = "Created a resource! Status: " + res.status + " --- Name: " + res.name
                              + " --- URI: " + res.uri;
        return Result.ok(resbuf);
    }

    @Service(desc = "This accesses a Python Google search resource and returns the result")
    public Result blahblah(HttpMethod method, String input)
    {
        HttpResult res;
        final Map<String, String> params = new HashMap<String, String>();
        params.put("query", "foo");
        res = accessResource("/resource/MyGoogleSearch/search", null, params);
        return new Result(res.status, res.data);
    }

    @Service(desc = "This returns Japanese message for test")
    public Result japanese(HttpMethod method, String input)
    {
        // This is a Japanese message (kore wa nihongo no message desu).
        final String message = "\u3053\u308c\u306f\u65e5\u672c\u8a9e\u306e\u30e1\u30c3\u30bb\u30fc\u30b8\u3067\u3059\u3002";
        return Result.ok(message);
    }
}
