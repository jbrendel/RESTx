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

import java.lang.annotation.Annotation;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;

import org.json.JSONException;
import org.mulesoft.restx.ResourceAccessorInterface;
import org.mulesoft.restx.RestxHttpRequest;
import org.mulesoft.restx.Settings;
import org.mulesoft.restx.component.api.ComponentDescriptor;
import org.mulesoft.restx.component.api.ComponentInfo;
import org.mulesoft.restx.component.api.Default;
import org.mulesoft.restx.component.api.FileStore;
import org.mulesoft.restx.component.api.HTTP;
import org.mulesoft.restx.component.api.HttpMethod;
import org.mulesoft.restx.component.api.HttpResult;
import org.mulesoft.restx.component.api.InputType;
import org.mulesoft.restx.component.api.InputTypes;
import org.mulesoft.restx.component.api.MakeResourceResult;
import org.mulesoft.restx.component.api.OutputType;
import org.mulesoft.restx.component.api.OutputTypes;
import org.mulesoft.restx.component.api.Parameter;
import org.mulesoft.restx.component.api.Choices;
import org.mulesoft.restx.component.api.ParamsInReqBody;
import org.mulesoft.restx.component.api.Service;
import org.mulesoft.restx.component.api.ServiceDescriptor;
import org.mulesoft.restx.exception.RestxException;
import org.mulesoft.restx.parameter.ParameterDef;
import org.mulesoft.restx.parameter.ParameterDefBoolean;
import org.mulesoft.restx.parameter.ParameterDefNumber;
import org.mulesoft.restx.parameter.ParameterDefString;
import org.mulesoft.restx.parameter.ParameterDefStringList;
import org.mulesoft.restx.parameter.ParameterDefNumberList;
import org.mulesoft.restx.util.JsonProcessor;
import org.mulesoft.restx.util.Url;

public abstract class BaseComponent
{
    public final String LANGUAGE = "JAVA";
    public ComponentDescriptor componentDescriptor = null;
    public ResourceAccessorInterface resourceAccessor;

    protected HashMap<String, Object> services;

    private RestxHttpRequest httpRequest;
    private String resourceName;
    private BaseComponentCapabilities baseCapabilities;

    private boolean annotationsHaveBeenParsed = false;
    // We use the following to record the order of parameters as well as their
    // Java types for each service when we are parsing the annotations. Later,
    // this helps our service-method calling proxy to arrange the parameters in
    // the right order - since Java does not allow the **fkwargs notation of named
    // parameters - and also allows us to do the necessary type casting.
    protected Map<String, ArrayList<String>> paramOrder;
    protected Map<String, ArrayList<Class<?>>> paramTypes;

    protected Map<String, String> instanceConf;

    protected BaseComponent()
    {
        this.resourceName = null;
        this.httpRequest = null;
        this.baseCapabilities = null;
        this.instanceConf = null;
    }

    public void setInstanceConf(Map<String, String> instanceConf)
    {
        this.instanceConf = instanceConf;
    }

    public void setBaseCapabilities(BaseComponentCapabilities baseCapabilities)
    {
        this.baseCapabilities = baseCapabilities;
    }

    private ComponentDescriptor getComponentDescriptor() throws RestxException
    {
        if (componentDescriptor == null)
        {
            initialiseComponentDescriptor();
        }
        return componentDescriptor;
    }

    public void setResourceName(String resourceName)
    {
        this.resourceName = resourceName;
    }

    public void setRequest(RestxHttpRequest request)
    {
        this.httpRequest = request;
    }

    public String getDocs()
    {
        return this.componentDescriptor.getDocs();
    }

    public String getRequestUri()
    {
        return httpRequest.getRequestURI();
    }

    public Map<String, List<String>> getRequestHeaders()
    {
        return httpRequest.getRequestHeaders();
    }

    public HttpResult accessResource(String uri)
    {
        return accessResource(uri, null, null, HTTP.GET);
    }

    public HttpResult accessResource(String uri, String input)
    {
        return accessResource(uri, input, null, HTTP.GET);
    }

    public HttpResult accessResource(String uri, String input, Map<?, ?> params)
    {
        return accessResource(uri, input, params, HTTP.GET);
    }

    public HttpResult accessResource(String uri, String input, Map<?, ?> params, HttpMethod method)
    {
        return resourceAccessor.accessResourceProxy(uri, input, params, method);
    }

    public MakeResourceResult makeResource(String componentClassName,
                                           String suggestedResourceName,
                                           String resourceDescription,
                                           boolean specialized,
                                           Map<?, ?> resourceParameters) throws RestxException
    {
        return resourceAccessor.makeResourceProxy(componentClassName, suggestedResourceName,
            resourceDescription, specialized, resourceParameters);
    }

    private ParameterDef createParamDefType(Class<?> paramType,
                                            String desc,
                                            boolean required,
                                            String defaultVal,
                                            String[] choices) throws RestxException
    {
        ParameterDef pdef = null;
        if (paramType == String.class)
        {
            pdef = new ParameterDefString(desc, required, defaultVal, choices);
        }
        else if (paramType == BigDecimal[].class) {
            BigDecimal defaultValue;
            if (defaultVal == null) {
                defaultValue = null;
            }
            else {
                defaultValue = new BigDecimal(defaultVal);
            }

            pdef = new ParameterDefNumberList(desc, required, defaultValue, choices);
        }
        else if (paramType == String[].class) {
            pdef = new ParameterDefStringList(desc, required, defaultVal, choices);
        }
        else if (paramType == Integer.class || paramType == BigDecimal.class || paramType == Double.class
                 || paramType == Float.class || paramType == int.class || paramType == float.class
                 || paramType == double.class)
        {
            BigDecimal defaultValue;
            if (defaultVal == null) {
                defaultValue = null;
            }
            else {
                defaultValue = new BigDecimal(defaultVal);
            }

            pdef = new ParameterDefNumber(desc, required, defaultValue, choices);
        }
        else if (paramType == Boolean.class)
        {
            pdef = new ParameterDefBoolean(desc, required, Boolean.valueOf(defaultVal));
        }
        return pdef;
    }

    protected void initialiseComponentDescriptor() throws RestxException

    {
        if (annotationsHaveBeenParsed || componentDescriptor != null)
        {
            return;
        }
        final Class<? extends BaseComponent> myclass = this.getClass();
        /*
         * Examine the class annotations to get information about the component.
         */
        final ComponentInfo ci = this.getClass().getAnnotation(ComponentInfo.class);
        if (ci == null)
        {
            throw new RestxException("Component does not have a ComponentInfo annotation");
        }
        componentDescriptor = new ComponentDescriptor(ci.name(), ci.desc(), ci.doc());

        /*
         * Examine field annotations to identify resource creation time parameters.
         */
        for (final Field f : myclass.getFields())
        {
            final Parameter fa = f.getAnnotation(Parameter.class);
            if (fa != null)
            {
                final String paramName = fa.name();
                final String paramDesc = fa.desc();
                String defaultVal = null;
                boolean required  = true;
                String[] choices  = null;

                // Check if we have a default value and set that one as well
                final Default fad = f.getAnnotation(Default.class);
                if (fad != null)
                {
                    defaultVal = fad.value();
                    required = false;
                }

                // Check if we have a list of choices
                final Choices cad = f.getAnnotation(Choices.class);
                if (cad != null)
                {
                    choices = cad.value();
                }
                final Class<?> ftype = f.getType();
                componentDescriptor.addParameter(paramName, createParamDefType(ftype, paramDesc, required, defaultVal, choices));
            }
        }

        /*
         * Examine the method annotations to identify service methods and their
         * parameters.
         */
        paramOrder = new HashMap<String, ArrayList<String>>();
        paramTypes = new HashMap<String, ArrayList<Class<?>>>();
        for (final Method m : myclass.getMethods())
        {
            if (m.isAnnotationPresent(Service.class))
            {
                final String serviceName = m.getName();
                final Service at = m.getAnnotation(Service.class);
                boolean pinreq = false;
                if (m.isAnnotationPresent(ParamsInReqBody.class))
                {
                    pinreq = true;
                }
                // Looking for output type annotations
                ArrayList<String> outputTypes = null;
                if (m.isAnnotationPresent(OutputType.class))
                {
                    final OutputType ot = m.getAnnotation(OutputType.class);
                    outputTypes = new ArrayList<String>();
                    outputTypes.add(ot.value());
                }
                if (m.isAnnotationPresent(OutputTypes.class))
                {
                    final OutputTypes ots = m.getAnnotation(OutputTypes.class);
                    final String[] otsSpecs = ots.value();
                    if (otsSpecs.length > 0)
                    {
                        if (outputTypes == null)
                        {
                            outputTypes = new ArrayList<String>();
                        }
                        for (final String ts : otsSpecs)
                        {
                            outputTypes.add(ts);
                        }
                    }
                }

                // Looking for output type annotations
                ArrayList<String> inputTypes = null;
                if (m.isAnnotationPresent(InputType.class))
                {
                    final InputType it = m.getAnnotation(InputType.class);
                    inputTypes = new ArrayList<String>();
                    final String it_val = it.value();
                    if (!it_val.equals(InputType.NO_INPUT))
                    {
                        inputTypes.add(it_val);
                    }
                    else {
                        inputTypes.add(null);
                    }
                }
                if (m.isAnnotationPresent(InputTypes.class))
                {
                    final InputTypes its = m.getAnnotation(InputTypes.class);
                    final String[] itsSpecs = its.value();
                    if (itsSpecs.length > 0)
                    {
                        if (inputTypes == null)
                        {
                            inputTypes = new ArrayList<String>();
                        }
                        for (final String ts : itsSpecs)
                        {
                            if (!ts.equals(InputType.NO_INPUT))
                            {
                                inputTypes.add(ts);
                            }
                            else {
                                inputTypes.add(null);
                            }
                        }
                    }
                }
                final ServiceDescriptor sd = new ServiceDescriptor(at.desc(), pinreq, outputTypes,
                    inputTypes);
                final Class<?>[] types = m.getParameterTypes();
                final Annotation[][] allParamAnnotations = m.getParameterAnnotations();
                int i = 0;
                final ArrayList<String> positionalParams = new ArrayList<String>();
                for (final Annotation[] pa : allParamAnnotations)
                {
                    String name = null;
                    String desc = null;
                    boolean required = true;
                    String defaultVal = null;
                    for (final Annotation a : pa)
                    {
                        if (a.annotationType() == Parameter.class)
                        {
                            name = ((Parameter) a).name();
                            desc = ((Parameter) a).desc();
                            if (!paramOrder.containsKey(serviceName))
                            {
                                paramOrder.put(serviceName, new ArrayList<String>());
                                paramTypes.put(serviceName, new ArrayList<Class<?>>());
                            }
                            if (((Parameter) a).positional())
                            {
                                positionalParams.add(name);
                            }
                            paramOrder.get(serviceName).add(name);
                            paramTypes.get(serviceName).add(types[i]);
                        }
                        else if (a.annotationType() == Default.class)
                        {
                            defaultVal = ((Default) a).value();
                            required = false;
                        }
                    }
                    if (name != null)
                    {
                        sd.addParameter(name, createParamDefType(types[i], desc, required, defaultVal, null));
                    }
                    ++i;
                }
                if (!positionalParams.isEmpty())
                {
                    sd.setPositionalParameters(positionalParams);
                }
                componentDescriptor.addService(m.getName(), sd);
            }
        }
        annotationsHaveBeenParsed = true;
    }

    public Map<String, ArrayList<String>> getParameterOrder() throws RestxException
    {
        initialiseComponentDescriptor();

        // Returns the order in which parameters were defined
        return paramOrder;
    }

    public Map<String, ArrayList<Class<?>>> getParameterTypes() throws RestxException
    {
        initialiseComponentDescriptor();

        // Returns the order in which parameters were defined
        return paramTypes;
    }

    public String getMyResourceName()
    {
        return resourceName;
    }

    public String getMyResourceUri()
    {
        return Settings.PREFIX_RESOURCE + "/" + getMyResourceName();
    }

    public FileStore getFileStorage()
    {
        return baseCapabilities.getFileStorage();
    }

    public FileStore getFileStorage(String namespace)
    {
        return baseCapabilities.getFileStorage(namespace);
    }

    public void httpSetCredentials(String accountName, String password)
    {
        baseCapabilities.httpSetCredentials(accountName, password);
    }

    public HttpResult httpGet(String url)
    {
        return baseCapabilities.httpGet(url);
    }

    public HttpResult httpGet(String url, Map<String, String> headers)
    {
        return baseCapabilities.httpGet(url, headers);
    }

    public HttpResult httpPost(String url, String data)
    {
        return baseCapabilities.httpPost(url, data);
    }

    public HttpResult httpPost(String url, String data, Map<String, String> headers)
    {
        return baseCapabilities.httpPost(url, data, headers);
    }

    // JSON processing
    public Object fromJson(String str) throws RestxException
    {
        try
        {
            return JsonProcessor.loads(str);
        }
        catch (final JSONException e)
        {
            throw new RestxException("Could not de-serialize data: " + e.getMessage());
        }
    }

    public String toJson(Object obj) throws RestxException
    {
        try
        {
            return JsonProcessor.dumps(obj);
        }
        catch (final JSONException e)
        {
            throw new RestxException("Could not serialize data: " + e.getMessage());
        }
    }

    private Map<String, Object> changeParamsToPlainDict(Map<String, ParameterDef> params)
    {
        final HashMap<String, Object> d = new HashMap<String, Object>();
        for (final Entry<String, ParameterDef> param : params.entrySet())
        {
            d.put(param.getKey(), param.getValue().asDict());
        }
        return d;
    }

    public Map<String, Object> getMetaData() throws RestxException, Exception
    {
        initialiseComponentDescriptor();

        final HashMap<String, Object> d = new HashMap<String, Object>();

        d.put("uri", new Url(getCodeUri()));
        d.put("name", getName());
        d.put("desc", getDesc());
        d.put("doc", getCodeUri() + "/doc");
        d.put("params", changeParamsToPlainDict(componentDescriptor.getParamMap()));
        d.put("services", _getServices(null));

        final HashMap<String, ParameterDef> rp = new HashMap<String, ParameterDef>();
        rp.put("suggested_name", new ParameterDefString(
            "Can be used to suggest the resource name to the server", true, ""));
        rp.put("desc", new ParameterDefString("Specifies a description for this new resource", false,
            "A '" + getName() + "' resource"));
        rp.put(
            "specialized",
            new ParameterDefBoolean(
                "Specifies if we want to create a specialized component resource (true) or a normal resource (false)",
                false, false));

        d.put("resource_creation_params", changeParamsToPlainDict(rp));

        return d;
    }

    public Map<String, ParameterDef> getParams() throws RestxException
    {
        if (componentDescriptor == null)
        {
            initialiseComponentDescriptor();
        }
        return componentDescriptor.getParamMap();
    }

    public String getName() throws RestxException
    {
        return getComponentDescriptor().getName();
    }

    public String getDesc() throws RestxException
    {
        return getComponentDescriptor().getDesc();
    }

    public String getDoc() throws RestxException
    {
        return getComponentDescriptor().getDocs();
    }

    public String getCodeUri()
    {
        String name;
        try
        {
            name = getName();
        }
        catch (final Exception e)
        {
            name = "";
        }
        return Settings.PREFIX_CODE + "/" + name;
    }

    /*
     * Following are some methods that are used by the framework and that are not
     * part of the official component-API.
     */

    /*
     * Return a dictionary of all defined services. resourceBaseUri may be set to
     * null, in which case all service URLs are relative to the code URL of the
     * component.
     */

    public Map<String, Object> _getServices(String resourceBaseUri) throws RestxException
    {
        initialiseComponentDescriptor();

        // Get the base URI for all services. If no resource base URI
        // was defined (can happen when we just look at code meta data)
        // then we use the code base URI instead.
        String baseUri;
        if (resourceBaseUri == null)
        {
            baseUri = getCodeUri();
        }
        else
        {
            baseUri = resourceBaseUri;
        }

        // Create a map of service descriptions.
        if (componentDescriptor.getServicMap() != null && !componentDescriptor.getServicMap().isEmpty())
        {
            services = componentDescriptor.getServicesAsPlainDict();
            final HashMap<String, Object> ret = new HashMap<String, Object>();
            for (final String name : services.keySet())
            {
                @SuppressWarnings("unchecked")
                final HashMap<String, Object> thisService = (HashMap<String, Object>) services.get(name);

                thisService.put("uri", new Url(baseUri + "/" + name));
                ret.put(name, thisService);

                @SuppressWarnings("unchecked")
                final HashMap<String, Object> params = (HashMap<String, Object>) thisService.get("params");

                if (params != null)
                {
                    for (final Entry<String, Object> param : params.entrySet())
                    {
                        final Object paramValue = param.getValue();
                        if (paramValue instanceof ParameterDef)
                        {
                            // Need the type check since we may have constructed the
                            // representation from storage, rather than in memory.
                            // If it's from storage then we don't have ParameterDefs
                            // in this dictionary here, so we don't need to convert
                            // anything.
                            final HashMap<String, Object> paramValueAsDict = ((ParameterDef) paramValue).asDict();
                            params.put(param.getKey(), paramValueAsDict);
                        }
                    }
                }
            }

            return ret;
        }
        else
        {
            // No services defined? Nothing to return...
            return null;
        }
    }
}
