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

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.Map;

import javax.script.Bindings;
import javax.script.ScriptEngine;
import javax.script.ScriptEngineManager;
import javax.script.ScriptException;

import org.mulesoft.restx.Settings;
import org.mulesoft.restx.component.BaseComponent;
import org.mulesoft.restx.component.api.ComponentDescriptor;
import org.mulesoft.restx.component.api.HTTP;
import org.mulesoft.restx.component.api.Result;
import org.mulesoft.restx.exception.RestxException;
import org.mulesoft.restx.parameter.ParameterType;

/**
 * Common infrastructure for all components written in a scripting language supported by a JSR-223-compatible engine.
 */
public abstract class BaseScriptingComponent extends BaseComponent
{
    private final ScriptEngineManager scriptEngineManager = new ScriptEngineManager();

    private ScriptEngine scriptEngine;

    protected Map<String, Object> resourceParams;

    /**
     * Create a new scripting engine for the particular language of the component.
     */
    protected abstract ScriptEngine newScriptEngine(ScriptEngineManager scriptEngineManager);

    /**
     * Get the script engine associated with this component's instance (or create a new one if there is none). RESTx
     * creates a new instance per request so the engine is not shared accross requests.
     */
    protected final ScriptEngine getOrCreateScriptEngine()
    {
        if (scriptEngine == null)
        {
            scriptEngine = newScriptEngine(scriptEngineManager);
        }

        return scriptEngine;
    }

    /**
     * Get the component source code as a stream. Override this method in a subclass if you need to augment the script
     * extra code.
     */
    protected InputStream getComponentCodeInputStream() throws FileNotFoundException
    {
        return new FileInputStream(getComponentScriptFile());
    }

    /**
     * Called by RESTx to initialize the component descriptor that contains the meta-data for the script component.
     */
    @Override
    protected final void initialiseComponentDescriptor() throws RestxException
    {
        if (componentDescriptor != null)
        {
            return;
        }

        componentDescriptor = getComponentDescriptor();
    }

    /**
     * Get the component descriptor for the script component.
     */
    protected abstract ComponentDescriptor getComponentDescriptor() throws RestxException;

    /**
     * Evaluate a script that is embedded with RESTx distribution and sits in the same directory as this class.
     */
    protected final Object evaluateEmbeddedScript(Bindings bindings, String resourceName)
        throws RestxException
    {
        return evaluate(bindings, BaseScriptingComponent.class.getResourceAsStream(resourceName),
            resourceName);
    }

    /**
     * Evaluate the component script with the provided bindings.
     */
    protected final Object evaluateComponent(Bindings bindings) throws RestxException
    {
        try
        {
            return evaluate(bindings, getComponentCodeInputStream(), getComponentScriptSourceContext());
        }
        catch (final FileNotFoundException fnfe)
        {
            throw new RestxException(fnfe.getMessage());
        }
    }

    /**
     * Add the commonly bound supported classes and values uses by all script components.
     */
    protected final void addCommonBindings(final Bindings bindings)
    {
        bindings.put("HTTP", new HTTP());
        bindings.put("TYPE", new ParameterType());
        bindings.put("RESULT", new Result(500, "No result provided"));
        bindings.put("RESTx", this);
    }

    /**
     * Called by RESTx to set the resource parameters.
     */
    public void _setResourceParams(Map<String, Object> resourceParams)
    {
        this.resourceParams = resourceParams;
    }

    /**
     * Called by RESTx when a particular service resource is accessed.
     */
    public abstract Object _serviceMethodDispatch(String methodName, Object[] args) throws RestxException;

    /**
     * For information purposes only. Override if getComponentCodeInputStream() has been overriden.
     */
    protected String getComponentScriptSourceContext()
    {
        return getComponentScriptFile().getPath();
    }

    private final File getComponentScriptFile()
    {
        return new File(Settings.getRootDir() + instanceConf.get("path"));
    }

    private Object evaluate(Bindings bindings, InputStream inputStream, String scriptSource)
        throws RestxException
    {
        try
        {
            final ScriptEngine engine = getOrCreateScriptEngine();
            return engine.eval(new InputStreamReader(inputStream), bindings);
        }
        catch (final ScriptException se)
        {
            throw new RestxException(se.getMessage() + " when executing script: " + scriptSource);
        }
    }
}
