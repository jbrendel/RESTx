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

package org.mulesoft.restx.util;

import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.json.JSONTokener;

/**
 * A service class that provides some static JSON processing methods.
 */
public class JsonProcessor
{
    /**
     * Serialize a complex object to JSON.
     * 
     * @param obj The object to be serialized. The object has to be a string, number
     *            or boolean, or a HashMap and/or ArrayList consisting of those basic
     *            types or further HashMaps and ArrayLists.
     * @return The JSON string representation of the object.
     */
    public static String dumps(Object obj) throws JSONException
    {
        if (obj instanceof Map<?, ?>)
        {
            // The JSON library offers a specific class for maps...
            return (new JSONObject(obj)).toString();
        }
        else if (obj instanceof Collection<?>)
        {
            // ... and another for arrays.
            return (new JSONArray(obj)).toString();
        }
        else
        {
            // But all other (normal) types are different. For some reason
            // the JSON library doesn't seem to handle this well.
            // So, we solve the issue by putting this other type of object
            // into a list, use JSONArray(), convert to string and strip off
            // the leading and trailing '[' and ']'. Then we have the proper
            // JSON-stype string representation of that type, which we can
            // return. This is extremely kludgy. One of these days we might
            // get around to fix this.
            // 
            final List<Object> al = new ArrayList<Object>();
            al.add(obj);
            final String buf = (new JSONArray(al)).toString();
            return buf.substring(1, buf.length() - 1);
        }
    }

    /**
     * Deserializes a JSON string into a complex object.
     * 
     * @param str A JSON string, representing a complex object.
     * @return A complex object, which will be a string, number or boolean, or a map
     *         or collection containing any of the other types.
     */
    public static Object loads(String str) throws JSONException
    {
        final JSONTokener t = new JSONTokener(str);
        return transcribe(t.nextValue());
    }

    /**
     * Transcribes a JSONObject into a map.
     * 
     * @param obj Instance of {@link JSONObject}.
     * @return A string representing the JSON serialization.
     * @throws JSONException
     */
    protected static Map<String, Object> jsonObjectTranscribe(JSONObject obj) throws JSONException
    {
        final Map<String, Object> d = new HashMap<String, Object>();
        final String[] nameArray = JSONObject.getNames(obj);

        if (nameArray != null)
        {
            for (final String name : JSONObject.getNames(obj))
            {
                d.put(name, transcribe(obj.get(name)));
            }
        }

        return d;
    }

    /**
     * Transcribes a JSONArray object into a Collection object.
     * 
     * @param arr A {@link JSONArray} instance.
     * @return A string representing the JSON serialization.
     * @throws JSONException
     */
    protected static Collection<?> jsonListTranscribe(JSONArray arr) throws JSONException
    {
        final List<Object> l = new ArrayList<Object>();
        for (int i = 0; i < arr.length(); ++i)
        {
            l.add(transcribe(arr.get(i)));
        }
        return l;
    }

    private static Object transcribe(Object o) throws JSONException
    {
        if (o instanceof JSONArray)
        {
            return jsonListTranscribe((JSONArray) o);
        }

        if (o instanceof JSONObject)
        {
            return jsonObjectTranscribe((JSONObject) o);
        }

        return o;
    }
}
