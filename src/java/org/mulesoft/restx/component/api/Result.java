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

package org.mulesoft.restx.component.api;

import java.util.HashMap;

/*
 * Inspired by the Result class defined for JAX-RS
 */
public class Result
{
    private int code;
    private Object data;
    private HashMap<String, String> headers;
    private String negotiatedType;

    public Result(int code, Object data)
    {
        this.code = code;
        this.data = data;
        this.headers = null;
        this.negotiatedType = null;
    }

    public Result addHeader(String name, String value)
    {
        if (headers == null)
        {
            headers = new HashMap<String, String>();
        }
        headers.put(name, value);
        return this;
    }

    @Override
    public String toString()
    {
        return "Result [code=" + code + ", data=" + data + ", headers=" + headers + ", negotiatedType="
               + negotiatedType + "]";
    }

    public static Result generic(int code, Object data)
    {
        return new Result(code, data);
    }

    public static Result ok()
    {
        return new Result(HTTP.OK, null);
    }

    public static Result ok(Object data)
    {
        return new Result(HTTP.OK, data);
    }

    public static Result created(String uri)
    {
        return created(uri, null);
    }

    public static Result created(String uri, Object obj)
    {
        final Result res = new Result(HTTP.CREATED, obj);
        res.addHeader("Location", uri);
        return res;
    }

    public static Result notFound(String message)
    {
        return new Result(HTTP.NOT_FOUND, message);
    }

    public static Result badRequest(String message)
    {
        return new Result(HTTP.BAD_REQUEST, message);
    }

    public static Result unauthorized(String message)
    {
        return new Result(HTTP.UNAUTHORIZED, message);
    }

    public static Result methodNotAllowed(String message)
    {
        return new Result(HTTP.METHOD_NOT_ALLOWED, message);
    }

    public static Result methodNotAllowed(HttpMethod httpMethod)
    {
        return methodNotAllowed("Method Not Allowed: " + httpMethod);
    }

    public static Result noContent()
    {
        return new Result(HTTP.NO_CONTENT, null);
    }

    public static Result temporaryRedirect(String uri)
    {
        final Result res = new Result(HTTP.TEMPORARY_REDIRECT, null);
        res.addHeader("Location", uri);
        return res;
    }

    public static Result internalServerError(String message)
    {
        return new Result(HTTP.INTERNAL_SERVER_ERROR, message);
    }

    public int getStatus()
    {
        return code;
    }

    public void setStatus(int code)
    {
        this.code = code;
    }

    public void setNegotiatedContentType(String negotiatedType)
    {
        this.negotiatedType = negotiatedType;
    }

    public String getNegotiatedContentType()
    {
        return negotiatedType;
    }

    public Object getEntity()
    {
        return data;
    }

    public void setEntity(Object data)
    {
        this.data = data;
    }

    public HashMap<String, String> getHeaders()
    {
        return headers;
    }
}
