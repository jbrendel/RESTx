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

/*
 * This is the JavaScript client library for RESTx.
 *
 * RESTx uses a simple RESTful API for all interactions. You don't
 * absolutely need to have this client library. However, it conveniently
 * encapsulates the common functionality around exploring, resource
 * creation and usage.
 *
 * Please take a look at the restx_js_client_example.js file to see how
 * these functions are used from within JavaScript.
 *
 * To see it all in action, start the RESTx server and send your browser
 * here: http://localhost:8001/static/restx/examples/restx_js_example_1.html
 *
 */

(function($) {

    $.restx = function(settings) {
        /* 
         * Initialisation of the client.
         * In this current version, you can ommit entering data for host and port as this will only
         * be of use when the RESTx server has been JSONP enabled and is able to do cross domain ajax calls
         * Examples:
         * for calling http://www.yourserver.com/path/to/your/application/yourproxypath/restxcommand
         *     your settings object should be
         *     {path: 'path/to/your/application', proxypath: 'yourproxypath'}
         */
        var config = {'host': '', 'port': 80, 'path': '', 'proxypath': '', 'errorCallback':function(data) {
            alert('This error message is shown by the default errorCallback method, please override in RESTx constructor.\nRESTx could not be initialized. \nUrl: '+data.url+'\nCause: '+data.error);
        }, 'code':'/code', 'resource': '/resource', 'specialized': '/specialized'};
        if (settings) $.extend(config, settings);

        this.url = '';
        if (config.host != '') {
            this.url += 'http://' + config.host;
            this.url += ':' + config.port;
        }
        if (config.path != '') this.url += '/' + config.path;
        if (config.proxypath != '') this.url += '/' + config.proxypath;

        /*
         * private method for verifying if the object {name:'', value:''} with the name 'paramName' is present in the params array
         */
        var isMissing = function(paramName, params) {
            for(var i = 0; i<params.length; i++) {
                if(params[i].name === paramName && params[i].value !== '') return false;
            }
            return true
        }

        /*
         * private method for verifying whether or not a mandatory parameter is missing
         * data is the json object returned by the RESTx sever
         * resource_creation_params is an array of {name:'', value:''} objects as created by jQuery's form.serializeArray() method
         * additional_params is an array of {name:'', value:''} objects as created by jQuery's form.serializeArray() method
         * returns null or an array of missing parameter names
         */
        var compare = function(data, resource_creation_params, additional_params) {
            //compare the data object from the server with both others
            var missingParams = [];
            var param_name;
            for(param_name in data['resource_creation_params']) {
                if(data['resource_creation_params'][param_name].required && isMissing(param_name, resource_creation_params))
                    missingParams.push(param_name);
            }
            if(additional_params) {
                for(param_name in data['params']) {
                    if(data['params'][param_name].required && isMissing(param_name, additional_params))
                        missingParams.push(param_name);
                }
            }
            if(missingParams.length === 0) return null;
            else return missingParams;
        }

        this.init = function(data) {
            config.code = data.code;
            config.resource = data.resource;
            config.specialized = data['specialized code'];
        }

                     
        /******************************************************************************************************************************    
         * fetches the server info from the RESTx server as a JSON object and injects this object in the callback method
         * callback = function that gets executed when the Ajax call to the RESTx server returns successfully
         * errorCallback = function that gets executed when the Ajax call to the RESTx server fails
         ********************************************************************************************************************************/
        this.getServerInfo = function(callback, errorCallback) {
            var currentUrl = this.url + '/';
            $.ajax({
                url: currentUrl,
                dataType: 'json',
                contentType: 'application/json',
                success:function(data) {
                        if(callback && typeof callback === 'function') callback(data);
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                        var test = '{"url": "'+currentUrl+'", "error": "'+XMLHttpRequest.status + '-' + XMLHttpRequest.statusText + '"}';
                        test = $.parseJSON(test); 
                        if(errorCallback && typeof errorCallback === 'function') errorCallback($.parseJSON('{"url": "'+currentUrl+'", "error": "'+XMLHttpRequest.status + '-' + XMLHttpRequest.statusText + '"}'));
                }
            });
        };
        this.getServerInfo(this.init, config.errorCallback);
        
        /****************************************************************************************************************************** 
         * Fetches a list of all components objects currently available on the RESTx server and injects this object list in the callback method
         * callback = function that gets executed when the Ajax call to the RESTx server returns successfully
         * errorCallback = function that gets executed when the Ajax call to the RESTx server fails
         ********************************************************************************************************************************/
        this.getAllComponentNamesPlus = function(callback, errorCallback, specialized) {
            if(specialized)
                var path = config.specialized;
            else
                var path = config.code;
            var currentUrl = this.url + path;
            $.ajax({
                url: currentUrl,
                dataType: 'json',
                contentType: 'application/json',
                success:function(data) {
                        if(callback && typeof callback === 'function') callback(data);
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                        var test = '{"url": "'+currentUrl+'", "error": "'+XMLHttpRequest.status + '-' + XMLHttpRequest.statusText + '"}';
                        test = $.parseJSON(test);
                        if(errorCallback && typeof errorCallback === 'function') errorCallback($.parseJSON('{"url": "'+currentUrl+'", "error": "'+XMLHttpRequest.status + '-' + XMLHttpRequest.statusText + '"}'));
                }
            });
        };
        
        /******************************************************************************************************************************     
         * Fetches a list of all components names currently available on the RESTx server and injects this list in the callback method
         * callback = function that gets executed when the Ajax call to the RESTx server returns successfully
         * errorCallback = function that gets executed when the Ajax call to the RESTx server fails
         ********************************************************************************************************************************/
        this.getAllComponentNames = function(callback, errorCallback, specialized) {
            if(specialized)
                var path = config.specialized;
            else
                var path = config.code;
            var currentUrl = this.url + path;
            var filter = function(data) {
                var newData = new Array();
                for(var propertyName in data) {
                    newData.push(propertyName);
                }
                if(callback && typeof callback === 'function') callback(newData);
            }
            $.ajax({
                url: currentUrl,
                dataType: 'json',
                contentType: 'application/json',
                success:function(data) {
                    filter(data);
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                        var test = '{"url": "'+currentUrl+'", "error": "'+XMLHttpRequest.status + '-' + XMLHttpRequest.statusText + '"}';
                        test = $.parseJSON(test);
                        if(errorCallback && typeof errorCallback === 'function') errorCallback($.parseJSON('{"url": "'+currentUrl+'", "error": "'+XMLHttpRequest.status + '-' + XMLHttpRequest.statusText + '"}'));
                }
            });
        };
        
        /****************************************************************************************************************************** 
         * Fetches the info for the named component from the RESTx server as a JSON object and injects this object in the callback method
         * componentName = name of the component you want the info about
         * callback = function that gets executed when the Ajax call to the RESTx server returns successfully
         * errorCallback = function that gets executed when the Ajax call to the RESTx server fails
         ********************************************************************************************************************************/
        this.getComponentDetails = function(componentName, callback, errorCallback, specialized) {
            if(specialized)
                var path = config.specialized;
            else
                var path = config.code;
            var currentUrl = this.url + path + '/' + componentName;
            if(!componentName || componentName === '') {
                if(errorCallback && typeof errorCallback === 'function') errorCallback($.parseJSON('{"url": "'+currentUrl+'", "error": "The mandatory \\\"componentName\\\" parameter was missing"}'));
            }
            else{
                $.ajax({
                    url: currentUrl,
                    dataType: 'json',
                    contentType: 'application/json',
                    success:function(data) {
                            if(callback && typeof callback === 'function') callback(data);
                    },
                    error: function(XMLHttpRequest, textStatus, errorThrown) {
                            var test = '{"url": "'+currentUrl+'", "error": "'+XMLHttpRequest.status + '-' + XMLHttpRequest.statusText + '"}';
                            test = $.parseJSON(test);
                            if(errorCallback && typeof errorCallback === 'function') errorCallback($.parseJSON('{"url": "'+currentUrl+'", "error": "'+XMLHttpRequest.status + '-' + XMLHttpRequest.statusText + '"}'));
                    }
                });
            }
        };
        
        /****************************************************************************************************************************** 
         * Fetches a list of all resources objects currently available on the RESTx server and injects this object list in the callback method
         * callback = function that gets executed when the Ajax call to the RESTx server returns successfully
         * errorCallback = function that gets executed when the Ajax call to the RESTx server fails
         ********************************************************************************************************************************/
        this.getAllResourceNamesPlus = function(callback, errorCallback) {
            var currentUrl = this.url + config.resource;
            $.ajax({
                url: currentUrl,
                dataType: 'json',
                contentType: 'application/json',
                success:function(data) {
                        if(callback && typeof callback === 'function') callback(data);
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                        var test = '{"url": "'+currentUrl+'", "error": "'+XMLHttpRequest.status + '-' + XMLHttpRequest.statusText + '"}';
                        test = $.parseJSON(test);
                        if(errorCallback && typeof errorCallback === 'function') errorCallback($.parseJSON('{"url": "'+currentUrl+'", "error": "'+XMLHttpRequest.status + '-' + XMLHttpRequest.statusText + '"}'));
                }
            });
        };
        
        /****************************************************************************************************************************** 
         * Fetches a list of all resources names currently available on the RESTx server and injects this list in the callback method
         * callback = function that gets executed when the Ajax call to the RESTx server returns successfully
         * errorCallback = function that gets executed when the Ajax call to the RESTx server fails
         ********************************************************************************************************************************/
        this.getAllResourceNames = function(callback, errorCallback) {
            var currentUrl = this.url + config.resource;
            var filter = function(data) {
                var newData = new Array();
                for(var propertyName in data) {
                    newData.push(propertyName);
                }
                if(callback && typeof callback === 'function') callback(newData);
            }
            $.ajax({
                url: currentUrl,
                dataType: 'json',
                contentType: 'application/json',
                success:function(data) {
                    filter(data);
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                        var test = '{"url": "'+currentUrl+'", "error": "'+XMLHttpRequest.status + '-' + XMLHttpRequest.statusText + '"}';
                        test = $.parseJSON(test);
                        if(errorCallback && typeof errorCallback === 'function') errorCallback($.parseJSON('{"url": "'+currentUrl+'", "error": "'+XMLHttpRequest.status + '-' + XMLHttpRequest.statusText + '"}'));
                }
            });
        }; 
        
        /****************************************************************************************************************************** 
         * Fetches the info for the named resource from the RESTx server as a JSON object and injects this object in the callback method
         * resourceName = name of the resource you want the info about
         * callback = function that gets executed when the Ajax call to the RESTx server returns successfully
         * errorCallback = function that gets executed when the Ajax call to the RESTx server fails
         ********************************************************************************************************************************/
        this.getResourceDetails = function(resourceName, callback, errorCallback) {
            var currentUrl = this.url + config.resource + '/' + resourceName;
            if(!resourceName || resourceName === '') {
                if(errorCallback && typeof errorCallback === 'function') errorCallback($.parseJSON('{"url": "'+currentUrl+'", "error": "The mandatory \\\"resourceName\\\" parameter was missing"}'));
            }
            else{
                $.ajax({
                    url: currentUrl,
                    dataType: 'json',
                    contentType: 'application/json',
                    success:function(data) {
                        if(callback && typeof callback === 'function') callback(data);
                    } ,
                    error: function(XMLHttpRequest, textStatus, errorThrown) {
                            var test = '{"url": "'+currentUrl+'", "error": "'+XMLHttpRequest.status + '-' + XMLHttpRequest.statusText + '"}';
                            test = $.parseJSON(test);
                            if(errorCallback && typeof errorCallback === 'function') errorCallback($.parseJSON('{"url": "'+currentUrl+'", "error": "'+XMLHttpRequest.status + '-' + XMLHttpRequest.statusText + '"}'));
                    }
                });
            }
        };

        /******************************************************************************************************************************
         * Fetches a list of all resources objects currently available on the RESTx server and injects this object list in the callback method
         * callback = function that gets executed when the Ajax call to the RESTx server returns successfully
         * errorCallback = function that gets executed when the Ajax call to the RESTx server fails
         ********************************************************************************************************************************/
        /*this.getAllSpecializedResourceNamesPlus = function(callback) {
            $.ajax({
                url: this.url + config.specialized,
                dataType: 'json',
                contentType: 'application/json',
                success:function(data) {
                        if(callback && typeof callback === 'function') callback(data);
                }
            });
        };*/

        /******************************************************************************************************************************
         * Fetches a list of all resources names currently available on the RESTx server and injects this list in the callback method
         * callback = function that gets executed when the Ajax call to the RESTx server returns successfully
         * errorCallback = function that gets executed when the Ajax call to the RESTx server fails
         ********************************************************************************************************************************/
        /*this.getAllSpecializedResourceNames = function(callback) {
            var filter = function(data) {
                var newData = new Array();
                for(var propertyName in data) {
                    newData.push(propertyName);
                }
                if(callback && typeof callback === 'function') callback(newData);
            }
            $.ajax({
                url: this.url + config.specialized,
                dataType: 'json',
                contentType: 'application/json',
                success:function(data) {
                    filter(data);
                }
            });
        };*/

        /******************************************************************************************************************************
         * Fetches the info for the named resource from the RESTx server as a JSON object and injects this object in the callback method
         * resourceName = name of the resource you want the info about
         * callback = function that gets executed when the Ajax call to the RESTx server returns successfully
         * errorCallback = function that gets executed when the Ajax call to the RESTx server fails
         ********************************************************************************************************************************/
        /*this.getSpecializedResourceDetails = function(resourceName, callback) {
            if(resourceName && resourceName !== '') {
                $.ajax({
                    url: this.url + config.specialized + resourceName,
                    dataType: 'json',
                    contentType: 'application/json',
                    success:function(data) {
                        if(callback && typeof callback === 'function') callback(data);
                    }
                });
            }
        };*/

        /******************************************************************************************************************************
         * Fetches the info for the named resource from the RESTx server as a JSON object and injects this object in the callback method
         * resourceName = name of the resource you want the info about
         * callback = function that gets executed when the Ajax call to the RESTx server returns successfully
         * errorCallback = function that gets executed when the Ajax call to the RESTx server fails
         ********************************************************************************************************************************/
        this.callService = function(resourceName, serviceName, callback, errorCallback) {
            var currentUrl = this.url + config.resource + '/' +     resourceName + '/' + serviceName;
            if(!resourceName && !serviceName) {
                if(errorCallback && typeof errorCallback === 'function') errorCallback($.parseJSON('{"url": "'+currentUrl+'", "error": "The mandatory \\\"resourceName\\\" and \\\"serviceName\\\" parameters were missing"}'));
            }
            else if(!resourceName) {
                if(errorCallback && typeof errorCallback === 'function') errorCallback($.parseJSON('{"url": "'+currentUrl+'", "error": "The mandatory \\\"resourceName\\\" parameter was missing"}'));
            }
            else if(!serviceName) {
                if(errorCallback && typeof errorCallback === 'function') errorCallback($.parseJSON('{"url": "'+currentUrl+'", "error": "The mandatory \\\"serviceName\\\" parameter was missing"}'));
            }
            if(resourceName && resourceName !== '' && serviceName && serviceName !== '') {
                $.ajax({
                    url: currentUrl,
                    dataType: 'json',
                    contentType: 'application/json',
                    success:function(data) {
                        if(callback && typeof callback === 'function') callback(data);
                    },
                    error: function(XMLHttpRequest, textStatus, errorThrown) {
                            var test = '{"url": "'+currentUrl+'", "error": "'+XMLHttpRequest.status + '-' + XMLHttpRequest.statusText + '"}';
                            test = $.parseJSON(test);
                            if(errorCallback && typeof errorCallback === 'function') errorCallback($.parseJSON('{"url": "'+currentUrl+'", "error": "'+XMLHttpRequest.status + '-' + XMLHttpRequest.statusText + '"}'));
                    }
                });
            }
        };
                                     
        /******************************************************************************************************************************
         *    This method creates a resource for a named component
         *    Creating a resource needs some information that is hidden in the 'options' object
         *    This options object should look like this:
         *    - componentName: (String) the name of the component that you want to create a resource for,
         *    - resource_creation_params: (Array of {name:'', value:''} objects) contains all parameters that are common to all resources
         *            currently these params are desc, suggested_name and specialized
         *    - additional_params: (Array of {name:'', value:''} objects) contains all parameters that are specific to this resource
         *    - success: a function that gets executed when the ajax call returns successfully
         *    - fail: a function that gets executed when the ajax call fails
         *    - validate: (boolean) if true, a check for presence of all mandatory parameters is executed before sending the call to the RESTx server
         ********************************************************************************************************************************/
        this.createResource = function(options) {
            var currentUrl = this.url+config.code+'/'+options.componentName;
            if(options.resource_creation_params.length === 0) {
                if(options.fail) options.fail($.parseJSON('{"url": "'+currentUrl+'", "error": "The mandatory \\\"resource_creation_params\\\" parameter was missing"}'));
            }
            else if(!options.componentName) {
                if(options.fail) options.fail($.parseJSON('{"url": "'+currentUrl+'", "error": "The mandatory \\\"componentName\\\" parameter was missing"}'));
            }
            else{
                var createResource = function() {
                    var jsonTyped = '{"resource_creation_params": {';
                    for(var i = 0; i < options.resource_creation_params.length; i++) {
                        jsonTyped += '"'+options.resource_creation_params[i].name+'":';
                        jsonTyped += '"'+options.resource_creation_params[i].value+'",';
                    }
                    jsonTyped = jsonTyped.substr(0, jsonTyped.length-1);
                    if(options.additional_params && options.additional_params.length>0) {
                        jsonTyped += '}, "params": {';
                        for(var i = 0; i < options.additional_params.length; i++) {
                            jsonTyped += '"'+options.additional_params[i].name+'":';
                            jsonTyped += '"'+options.additional_params[i].value+'",';
                        }
                        jsonTyped = jsonTyped.substr(0, jsonTyped.length-1);
                    }
                    jsonTyped += '}}';
                    $.ajax({
                        url:currentUrl,
                        type: 'POST',
                        data:jsonTyped,
                        success:function(data, textStatus, XMLHttpRequest) {
                            options.success($.parseJSON(jsonTyped));
                        },
                        error: function(XMLHttpRequest, textStatus, errorThrown) {
                            options.fail($.parseJSON('{url": "'+currentUrl+'", "error": "'+XMLHttpRequest.status + '-' + XMLHttpRequest.statusText + '"}'));
                        }
                    });
                }
                if(options.validate) {
                    $.ajax({
                        url: currentUrl,
                        dataType: 'json',
                        contentType: 'application/json',
                        success:function(data) {
                            var missingParameter = compare(data, options.resource_creation_params, options.additional_params);
                            if(!missingParameter) {
                                createResource();
                            }
                            else
                                options.fail($.parseJSON('{"url": "'+currentUrl+'", "error": "Error during the validation process! The mandatory parameter(s) \\\"'+missingParameter+'\\\" was/were missing from the resource_creation_params or the additional_params"}'));
                        },
                        error: function(XMLHttpRequest, textStatus, errorThrown) {
                            options.fail($.parseJSON('{url": "'+currentUrl+'", "error": "Error during the validation process! '+XMLHttpRequest.status + '-' + XMLHttpRequest.statusText + '"}'));
                        }
                    });
                }
                else
                    createResource();
            }
        }

        return this;

    };

})(jQuery);


