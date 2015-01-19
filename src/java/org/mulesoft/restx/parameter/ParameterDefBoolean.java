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

public class ParameterDefBoolean extends ParameterDef
{
    private final boolean defaultVal;

    public ParameterDefBoolean(String desc)
    {
        this(desc, true, false);
    }

    public ParameterDefBoolean(String desc, boolean required, boolean defaultVal)
    {
        super(ParameterType.BOOLEAN, desc, required);
        this.defaultVal = defaultVal;
    }

    @Override
    public Object getDefaultVal()
    {
        return defaultVal;
    }

    @Override
    public String html_type(String name, String initial) // strange naming? This is called from
                                                         // Python code as well
    {
        String yes_value = "";
        String no_value  = "";
        if (initial != null  &&  initial.length() > 0) {
            if (initial.equals("yes")) {
                yes_value = " checked";
            }
            if (initial.equals("no")) {
                no_value = " checked";
            }
        }
            
        final String ret = "<label for=" + name + "_yes><input" + yes_value + " type=radio id=" + name + "_yes name=" + name
                           + " value=yes />yes</label><br>";

        return ret + "<label for=" + name + "_no><input" + no_value + " type=radio id=" + name + "_no name=" + name
               + " value=no />no</label><br>";
    }

    @Override
    public Class<?> getJavaType()
    {
        return Boolean.class;
    }
}
