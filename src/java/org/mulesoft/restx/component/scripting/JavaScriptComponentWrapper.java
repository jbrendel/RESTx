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

package org.mulesoft.restx.component.scripting;

import java.io.FileNotFoundException;
import java.io.InputStream;
import java.io.SequenceInputStream;
import java.util.ArrayList;
import java.util.HashMap;

import javax.script.Bindings;
import javax.script.Invocable;
import javax.script.ScriptContext;
import javax.script.ScriptEngine;
import javax.script.ScriptEngineManager;
import javax.script.ScriptException;
import javax.script.SimpleBindings;

import org.mulesoft.restx.component.api.ComponentDescriptor;
import org.mulesoft.restx.exception.RestxException;

/**
 * Handler for JavaScript components that acts as a wrapper around the script and connects it to the RESTx host
 * infrastructure.
 */
public class JavaScriptComponentWrapper extends BaseScriptingComponent
{
    private static final String BASE_COMPONENT_JS = "base_component.js";

    @Override
    protected ScriptEngine newScriptEngine(ScriptEngineManager scriptEngineManager)
    {
        return scriptEngineManager.getEngineByName("javascript");
    }

    @Override
    protected InputStream getComponentCodeInputStream() throws FileNotFoundException
    {
        // for JS, we wire-in a base_component with helper functions
        return new SequenceInputStream(getClass().getResourceAsStream(BASE_COMPONENT_JS),
            super.getComponentCodeInputStream());
    }

    @Override
    protected String getComponentScriptSourceContext()
    {
        return BASE_COMPONENT_JS + " concatenated with " + super.getComponentScriptSourceContext();
    }

    @SuppressWarnings("unchecked")
    @Override
    protected ComponentDescriptor getComponentDescriptor() throws RestxException
    {
        final Bindings bindings = new SimpleBindings();
        addCommonBindings(bindings);

        // load the component metadata into bindings
        evaluateComponent(bindings);

        // extract a component descriptor out of these bindings
        evaluateEmbeddedScript(bindings, "configuration_loader.js");

        paramOrder = (HashMap<String, ArrayList<String>>) bindings.get("paramOrder");
        paramTypes = (HashMap<String, ArrayList<Class<?>>>) bindings.get("paramTypes");

        return (ComponentDescriptor) bindings.get("componentDescriptor");
    }

    @Override
    public Object _serviceMethodDispatch(String methodName, Object[] args) throws RestxException
    {
        try
        {
            final ScriptEngine engine = getOrCreateScriptEngine();
            final Bindings bindings = engine.getBindings(ScriptContext.ENGINE_SCOPE);
            addCommonBindings(bindings);

            // must evaluate first before calling a function directly
            evaluateComponent(bindings);

            // bind the resource parameters before calling the function
            bindings.putAll(resourceParams);
            final Invocable invocable = (Invocable) engine;
            final Object jsResult = invocable.invokeFunction(methodName, args);

            // post process the result to transform native JS objects into Java data
            // structures
            final Object result = invocable.invokeFunction("_postProcessResult", jsResult);
            return result;
        }
        catch (final ScriptException se)
        {
            throw new RestxException(se.getMessage());
        }
        catch (final NoSuchMethodException nsme)
        {
            throw new RestxException(nsme.getMessage());
        }
    }
}
