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

import java.util.ArrayList;
import java.util.HashMap;

public abstract class ParameterDef
{
    public String ptype;
    public String desc;
    public boolean required;

    protected String[] choices = null;

    public ParameterDef(String ptype, String desc, boolean required)
    {
        this.ptype = ptype;
        this.desc = desc;
        this.required = required;
    }

    public abstract Object getDefaultVal();

    public HashMap<String, Object> asDict()
    {
        final HashMap<String, Object> d = new HashMap<String, Object>();

        d.put("type", ptype);
        d.put("desc", desc);
        d.put("required", required);
        if (!required)
        {
            d.put("default", getDefaultVal());
        }

        if (choices != null)
        {
            final ArrayList<String> clist = new ArrayList<String>();
            for (final String s : choices)
            {
                clist.add(s);
            }
            d.put("val_choices", clist);
            if (isList())
            {
                d.put("multi_choice", true);
            }
        }

        return d;
    }

    public boolean isList()
    {
        return false;
    }

    public String html_type(String name, String initial) // strange naming? This is called from
    // Python code as well
    {
        String init_val = " ";
        if (initial != null && initial.length() > 0)
        {
            init_val = " value=\"" + initial + "\" ";
        }

        if (choices != null)
        {
            final StringBuilder buf = new StringBuilder("<select name=" + name + " id=" + name + " >");

            if (!this.required)
            {
                // If we are not required then we definitely have a default value
                buf.append("<option value=\"\">--- Accept default ---</option>");
            }

            for (final String c : choices)
            {
                String args = "";
                if ((initial != null) && (c.equals(initial)))
                {
                    args = " selected=\"selected\"";
                }
                buf.append("<option value=\"")
                    .append(c)
                    .append("\"")
                    .append(args)
                    .append(">")
                    .append(c)
                    .append("</option>");
            }
            buf.append("</select>");
            return buf.toString();
        }

        return "<input type=text name=" + name + " id=" + name + init_val + "/>";
    }

    public abstract Class<?> getJavaType();

}
