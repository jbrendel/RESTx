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

import java.util.Map;

import org.mulesoft.restx.component.api.HttpMethod;
import org.mulesoft.restx.component.api.HttpResult;
import org.mulesoft.restx.component.api.MakeResourceResult;

public interface ResourceAccessorInterface
{
    public HttpResult         accessResourceProxy(String uri, String input, Map<?,?> params, HttpMethod method);
    public MakeResourceResult makeResourceProxy(String componentClassName, String suggestedResourceName,
                                                String resourceDescription, boolean specialized, Map<?,?> resourceParameters);
}


