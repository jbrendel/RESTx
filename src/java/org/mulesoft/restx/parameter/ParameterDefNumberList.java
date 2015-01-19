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

import java.math.BigDecimal;
import java.math.BigInteger;
import java.util.List;

import org.mulesoft.restx.exception.RestxException;

public class ParameterDefNumberList extends ParameterDefList
{
    private final BigDecimal defaultVal;

    public ParameterDefNumberList(String desc)
    {
        this(desc, true, null);
    }

    public ParameterDefNumberList(String desc, float defaultVal)
    {
        this(desc, false, defaultVal);
    }

    public ParameterDefNumberList(String desc, BigDecimal defaultVal)
    {
        this(desc, false, defaultVal);
    }

    public ParameterDefNumberList(String desc, boolean required, Number defaultVal)
    {
        super(ParameterType.NUMBER_LIST, desc, required);
        this.defaultVal = toBigDecimal(defaultVal);
    }

    public ParameterDefNumberList(String desc, boolean required, Number defaultVal, String[] choices)
        throws RestxException
    {
        super(ParameterType.NUMBER_LIST, desc, required);
        this.defaultVal = toBigDecimal(defaultVal);
        if (choices != null)
        {
            processChoices(choices);
        }
    }

    private void processChoices(String[] choices) throws RestxException
    {
        final String strChoices[] = new String[choices.length];

        int i = 0;
        boolean foundDefault = false;
        for (final String bvStr : choices)
        {
            final BigDecimal bv = new BigDecimal(bvStr);
            if (defaultVal != null)
            {
                if (bv.compareTo((this.defaultVal)) == 0)
                {
                    foundDefault = true;
                }
            }
            strChoices[i++] = bv.toString();
        }
        if (defaultVal != null && !foundDefault)
        {
            throw new RestxException("Specified default value is not listed in 'choices'");
        }
        this.choices = strChoices;
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

    private BigDecimal toBigDecimal(Number defaultVal)
    {
        if (defaultVal instanceof BigDecimal)
        {
            return (BigDecimal) defaultVal;
        }
        else if (defaultVal instanceof BigInteger)
        {
            return new BigDecimal((BigInteger) defaultVal);
        }
        else if (defaultVal instanceof Float)
        {
            return BigDecimal.valueOf(defaultVal.floatValue());
        }
        else if (defaultVal instanceof Double)
        {
            return BigDecimal.valueOf(defaultVal.doubleValue());
        }
        else if (defaultVal instanceof Long)
        {
            return BigDecimal.valueOf(defaultVal.longValue());
        }
        else if (defaultVal instanceof Integer)
        {
            return BigDecimal.valueOf(defaultVal.intValue());
        }

        return null;
    }

    public static Number[] listToArray(List<BigDecimal> obj)
    {
        final BigDecimal[] d = new BigDecimal[obj.size()];
        for (int i = 0; i < obj.size(); ++i)
        {
            d[i] = obj.get(i);
        }
        return d;
    }

    @Override
    public Class<?> getJavaType()
    {
        return BigDecimal.class;
    }
}
