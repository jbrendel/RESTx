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

package org.mulesoft.restx;

import java.util.List;

import org.python.core.PyFunction;
import org.python.core.PyObject;
import org.python.util.PythonInterpreter;

public class Settings
{
    private static PyFunction get_root_dir = null;

    /*
     * Eventually this will provide access to all config parameters. In the meantime,
     * it uses some Jython specifics to get access to the configs that are stored in
     * settings.py
     */

    /*
     * Our handle on the Python interpreter. It is initialized in the static
     * initializer and then re-used in the getFromPythonSettings() method.
     */
    private static PythonInterpreter interp;

    /*
     * Used to initialize individual Java class members with values from the Python
     * settings.py module. For strings.
     */
    private static String getStringFromPythonSettings(String objName)
    {
        final PyObject pyObject = interp.get(objName);
        return (String) pyObject.__tojava__(String.class);
    }

    /*
     * Used to initialize individual Java class members with values from the Python
     * settings.py module. For lists of strings.
     */
    private static List<?> getListFromPythonSettings(String objName)
    {
        final PyObject pyObject = interp.get(objName);
        final List<?> poList = (List<?>) pyObject.__tojava__(List.class);
        return poList;
    }

    /*
     * Initialize and import only once.
     */
    static
    {
        interp = new PythonInterpreter();
        interp.exec("from restx.settings import *");
        interp.exec("from restx.render import DEFAULT_OUTPUT_TYPES");
        interp.exec("from restx.render import DEFAULT_INPUT_TYPES");
        get_root_dir = interp.get("get_root_dir", PyFunction.class);
    }

    /*
     * Here finally we have the publicly exported symbols.
     */
    public static String DOCUMENT_ROOT = getStringFromPythonSettings("DOCUMENT_ROOT");
    public static String PREFIX_CODE = getStringFromPythonSettings("PREFIX_CODE");
    public static String PREFIX_RESOURCE = getStringFromPythonSettings("PREFIX_RESOURCE");
    public static List<?> DEFAULT_OUTPUT_TYPES = getListFromPythonSettings("DEFAULT_OUTPUT_TYPES");
    public static List<?> DEFAULT_INPUT_TYPES = getListFromPythonSettings("DEFAULT_INPUT_TYPES");

    public static String getRootDir()
    {
        return (String) (get_root_dir.__call__().__tojava__(String.class));
    }
}
