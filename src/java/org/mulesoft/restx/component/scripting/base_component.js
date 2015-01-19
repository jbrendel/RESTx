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

// functions are prefixed with _ because they get loaded side by side with user's JS component

function _isPureObject(obj) {
    if (!(obj instanceof Object)) return false
    
    for (m in obj) {
        if (typeof(obj[m]) == 'function') return false;
    }
    
    return true
}

function _jsDatastructuresToJava(datastructure) {
    if (datastructure instanceof Array) {
        var list = new java.util.ArrayList()
        for (i in datastructure) {
            list.add(_jsDatastructuresToJava(datastructure[i]))
        }
        return list
    } else if (_isPureObject(datastructure)) {
        var map = new java.util.HashMap()
        for (k in datastructure) {
            map.put(k, _jsDatastructuresToJava(datastructure[k]))
        }
        return map
    }
    
    return datastructure
}

function _postProcessResult(result) {
    result.setEntity(_jsDatastructuresToJava(result.getEntity()))
    return result
}
