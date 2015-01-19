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

package org.mulesoft.restx.parameter;

import java.util.List;

import org.mulesoft.restx.exception.RestxException;

public class ParameterDefStringList extends ParameterDefList
{
    private final String defaultVal;

    public ParameterDefStringList(String desc)
    {
        this(desc, true, (String) null);
    }

    public ParameterDefStringList(String desc, boolean required, String defaultVal)
    {
        super(ParameterType.STRING_LIST, desc, required);
        this.defaultVal = defaultVal;
    }

    public ParameterDefStringList(String desc, boolean required, String[] choices) throws RestxException
    {
        this(desc, required, null, choices);
    }

    public ParameterDefStringList(String desc, boolean required, String defaultVal, String[] choices)
        throws RestxException
    {
        super(ParameterType.STRING_LIST, desc, required);
        this.defaultVal = defaultVal;
        if (defaultVal != null && choices != null)
        {
            boolean foundDefault = false;
            for (final String s : choices)
            {
                if (s.equals(defaultVal))
                {
                    foundDefault = true;
                    break;
                }
            }
            if (!foundDefault)
            {
                throw new RestxException("Specified default value is not listed in 'choices'");
            }
        }
        this.choices = choices;
    }

    public String html_type(String name, List<?> initial)
    {
        // Need to convert the list of numbers to list of strings
        final String[] initialStrs = new String[initial.size()];
        for (int i = 0; i < initial.size(); ++i)
        {
            initialStrs[i] = initial.get(i).toString();
        }
        return this.html_type(name, initialStrs);
    }

    @Override
    public Object getDefaultVal()
    {
        return defaultVal;
    }

    @Override
    public Class<?> getJavaType()
    {
        return String.class;
    }
}
