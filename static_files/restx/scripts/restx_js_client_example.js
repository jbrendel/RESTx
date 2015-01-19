/*            
 * RESTx: Sane, simple and effective data publishing and integration. 
 *    
 * Copyright (C) 2010     MuleSoft Inc.        http://www.mulesoft.com 
 *    
 * This program is free software: you can redistribute it and/or modify 
 * it under the terms of the GNU General Public License as published by 
 * the Free Software Foundation, either version 3 of the License, or 
 * (at your option) any later version. 
 * 
 * This program is distributed in the hope that it will be useful, 
 * but WITHOUT ANY WARRANTY; without even the implied warranty of 
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the 
 * GNU General Public License for more details. 
 * 
 * You should have received a copy of the GNU General Public License 
 * along with this program.    If not, see <http://www.gnu.org/licenses/>. 
 */

/*
 * This is the example code that uses the JavaScript client library for RESTx.
 *
 * To see it all in action, start the RESTx server and send your browser
 * here: http://localhost:8001/static/restx/examples/restx_js_example_1.html
 *
 */

// Creating a namespace
var mule = {};

// small utility method for detecting whether or not this object is an array
mule.isArray = function(obj) {
    return (obj.constructor.toString().indexOf('Array') != -1);
}

// private method for creating a dom object out of the returned JSON object
// this method is called recurrently
mule.getObjectInfo = function(currentString, propName, ob) {
    if(ob) {
        if(typeof ob === 'string') return currentString += '<li>' + propName +': '+ob+'</li>';
        else if(mule.isArray(ob)) {
            //var untilString = currentString;
            for(var i = 0; i<ob.length; i++) {
                currentString += mule.getObjectInfo("", propName+'['+i+']', ob[i]);
            }
            return '<ul>'+currentString+'</ul>';
        }
        else{
            currentString += '<li>' + propName + '</li><ul>';
            for(var propertyName in ob) {
                currentString = mule.getObjectInfo(currentString, propertyName, ob[propertyName])
            }
            return currentString + "</ul>";
        }
    }
    else{
        return currentString += '<li>' + propName +': null</li>';
    }
}

// private method for writing out the returned json object to the dom tree
mule.myLogging = function(data, objectname) {
        $('#result').empty();
        try{
                var info = '<ul>';
                info += mule.getObjectInfo(info, objectname, data);
                $('#result').append(info+'</ul>');
        }catch(e) {
            var test = e;
                alert(e.message);
        }
};

// private method for writing out the returned json object to the dom tree
mule.myErrorLogging = function(data, objectname) {
        $('#result').empty();
        try{
                var info = '<h2 style="color:red; font-weight:bold; font-size:18px">';
                info += 'There was a problem with the ' + objectname + ' process.<br/>- Url: ' + data.url + '<br/>- Cause: ' + data.error;
                $('#result').append(info+'</h2>');
        }catch(e) {
            var test = e;
                alert(e.message);
        }
};


/*
 * private method that gets executed when the user retrieves the newly created resource
 * one by one, the names of all available services are added as option elements to the empty "step7" select block
 */
mule.showServices = function(data, componentName) {
    mule.myLogging(data, componentName);
    var dom = '';
    for(var servicename in data.services) {
            dom += '<option>' + servicename +'</option>';
    }
    $("#step7").empty().append(dom);
};

/*
 * private method that gets executed when the ResourceCreation call returns successfully
 * A victory message is shown in the #result box and
 * 'Step 6', a link to the 'getResourceDetails' method, is created for this new resource
 */
mule.resourceCreationSuccessCallback = function(componentname, jsonob) {
    $('#result').empty();
    $("#result").append("<h3>YES! The resource '"+componentname+"' was created successfully.</h3>");
    if(jsonob.resource_creation_params.specialized && jsonob.resource_creation_params.specialized === 'on')
        alert("You've created a specialized object therefore it will not be called back for usage.");
    else{
        var linkId = Math.floor(Math.random() * 10000) + 10000;
        $("#newresource").empty().append("<a href='#' id='res_"+linkId+"'>Execute Step 6</a>");
        $("#res_"+linkId).click(function(e) {
            e.preventDefault();
            mule.currentResource = jsonob.resource_creation_params.suggested_name;
            mule.myrestx.getResourceDetails(jsonob.resource_creation_params.suggested_name,
                function(data) {
                    mule.myLogging(data, componentname);
                    mule.showServices(data, componentname);
                },
                function(data) {
                    mule.myErrorLogging(data, 'RESTx Server')
                });
        });
    }
};

/*
 * private method that gets executed when the ResourceCreation call fails
 * A fail message is shown in the #result box
 */
mule.resourceCreationFailCallback = function(componentname, jsonob) {
    alert('Oh boy! Something went wrong while creating the resource '+componentname+'\n'+jsonob.error);
    mule.myErrorLogging(jsonob, componentname);
    /*$('#result').empty();
    $("#result").append("<h3>Oh boy! Something went wrong while creating the resource '"+componentname+"'.</h3>").
        append("<br />").append("<h3>"+jsonob.error+"</h3>");*/
};

/*
 * private method that gets executed when the getComponentDetails method returns successfully
 * An html form is created that contains formfields for all parameters (mandatory and optional, common and specific))
 * the submit event of this form is intercepted and is converted into an ajax POST call to RESTx
 * the success and fail methods of this POST call are defined here above
 */
mule.buildResourceCreationForm = function(componentName, data) {
    //Show the data in the page
    mule.myLogging(data, componentName);

    //Create a random number that will be used as id for this form
    var formId = Math.floor(Math.random() * 10000) + 10000;

    //Start writing to the dom
    var dom = '<div style="position:relative;width:inherit"><form action="'+mule.myrestx.url+'/resource/_createResourceForm/create/'+componentName+'" method="POST" id="mule_' + formId + '" name="input">';
    var required;
    //Looping through the common component parameters
    for (var name in data.resource_creation_params) {
        required = '';
        if (data.resource_creation_params.hasOwnProperty(name)) {
            if(data.resource_creation_params[name].required) required = '<span class="mule_required"></span>';
            if (data.resource_creation_params[name].type === 'boolean') {
                dom += '<div style="width:48%;float:left;"><div class=mule_label><label for="resource_creation_params__' + name + '">' + name + ':</label></div><div class="mule_info">('+data.resource_creation_params[name].desc+')</div></div>';
                dom += '<div style="width:48%;float:left;"><input type="checkbox" name="resource_creation_params__' + name + '" id="resource_creation_params__' + name + '" />'+required+'</div>';
            }
            else {
                dom += '<div style="width:48%;float:left;"><div class=mule_label><label for="resource_creation_params__' + name + '">' + name + ':</label></div><div class="mule_info">('+data.resource_creation_params[name].desc+')</div></div>';
                dom += '<div style="width:48%;float:left;"><input type="text" name="resource_creation_params__' + name + '" id="resource_creation_params__' + name + '" />'+required+'</div>';
            }
            dom += '<div style="clear:both"></div>';
        }
    }
    //Looping through the component specific parameters
    for (name in data.params) {
        required = '';
        if (data.params.hasOwnProperty(name)) {
            if(data.params[name].required) required = '<span class="mule_required"></span>';
            if (data.params[name].type === 'boolean') {
                dom += '<div style="width:48%;float:left;"><div class=mule_label><label for="params__' + name + '">' + name + ':</label></div><div class="mule_info">('+data.params[name].desc+')</div></div>';
                dom += '<div style="width:48%;float:left;"><input type="checkbox" name="params__' + name + '" id="params__' + name + '" />'+required+'</div>';
            }
            else {
                dom += '<div style="width:48%;float:left;"><div class=mule_label><label for="params__' + name + '">' + name + ':</label></div><div class="mule_info">('+data.params [name].desc+')</div></div>';
                dom += '<div style="width:48%;float:left;"><input type="text" name="params__' + name + '" id="params__' + name + '" />'+required+'</div>';
            }
            dom += '<div style="clear:both"></div>';

        }
    }
    dom += '<div><input type="submit" value="Execute Step 4" /></div>';
    dom += '</form></div>';
    $('#resourceform').empty().append($(dom));

    //Creating the 'form submit' interception
    $('#mule_'+formId).submit(function(e) {
        e.preventDefault();
        $("#messageload").empty().append($(this).serialize());
        var dataArray = $(this).serializeArray();

        var resource_creation_params = [];
        var additional_params = [];
        for(var i = 0; i < dataArray.length; i++) {
            if(dataArray[i].name.indexOf('resource_creation_params') >= 0) {
                dataArray[i].name = dataArray[i].name.substring(26);
                if(dataArray[i].value != '') resource_creation_params.push(dataArray[i]);
            }
            else{
                dataArray[i].name = dataArray[i].name.substring(8);
                if(dataArray[i].value != '') additional_params.push(dataArray[i]);
            }
        }

        //Create the options object that is the parameter for the 'createResource' method call
        var options = {
            componentName: componentName,
            resource_creation_params: resource_creation_params,
            additional_params: additional_params,
            success: function(jsonOb) {
                mule.resourceCreationSuccessCallback(componentName, jsonOb);
            },
            fail: function(jsonOb) {
                mule.resourceCreationFailCallback(componentName, jsonOb);
            },
            validate: true
        };

        //Do the ajax call to finalise the onSubmit event method
        mule.myrestx.createResource(options);
    });
};

/*
 * private method that gets executed when the callService method returns successfully
 * in this implementation, it's just a wrapper around the myLogging method 
 */
mule.showServicecallResult = function(resourceName, serviceName, data) {
    //Show the data in the page
    mule.myLogging(data, resourceName+'/'+serviceName);
};

/*
 * private method that gets executed when the ResourceCreationForm has been created. It checks for the presence
 * of dom elements having the 'mule_required' class. If it finds any, it writes a '(*)' in its content
 */
mule.showRequired = function() {
    $('.mule_required').each(function() {
        $(this).text('(*)');
    })
};

//private wrapper method that calls the private buildResourceCreationForm and the private showRequired methods
mule.doResourceFormBuild = function(componentName, data) {
    mule.buildResourceCreationForm(componentName, data);
    mule.showRequired();
}


/*
 * private method that gets executed when the user clicks the "Step 1" link and the RESTx "getComponents" call returns successfully.
 * One by one, all componentnames are added as option elements to the empty "step2" select block
 */
mule.showComponents = function(data) {
    mule.myLogging(data, 'RESTx server');
    var dom = '';
    for(var i = 0; i < data.length; i++) {
            dom += '<option>' + data[i] +'</option>';
    }
    $("#step2").empty().append(dom);

};

// START Executing JavaScript from here
$(document).ready(function() {
        mule.myrestx = $.restx({proxypath: $("#proxypath").val()});
        $("#proxysetter").click(function(e) {
                mule.myrestx = $.restx({proxypath: $("#proxypath").val()});
        });
        $('#serverInfo').click(function(e) {
                e.preventDefault();
                //Calling public method getServerInfo and injecting the JSON result in the mule.myLogging method
                mule.myrestx.getServerInfo(
                    function(data) {
                        mule.myLogging(data, 'RESTx Server');
                    },
                    function(data) {
                        mule.myErrorLogging(data, 'RESTx Server');
                    });
        });
        $('#resource').click(function(e) {
                e.preventDefault();
                //Calling public method getAllResourceNames and injecting the JSON result in the mule.myLogging method
                mule.myrestx.getAllResourceNames(
                    function(data) {
                        mule.myLogging(data, 'RESTx Server Resources');
                    },
                    function(data) {
                        mule.myErrorLogging(data, 'RESTx Server');
                    });
        });
        $('#resourcePlus').click(function(e) {
                e.preventDefault();
                //Calling public method getAllResourceNames and injecting the JSON result in the mule.myLogging method
                mule.myrestx.getAllResourceNamesPlus(
                    function(data) {
                        mule.myLogging(data, 'RESTx Server Resources');
                    },
                    function(data) {
                        mule.myErrorLogging(data, 'RESTx Server');
                    });
        });
        $('#specializedComponentPlus').click(function(e) {
                e.preventDefault();
                //Calling public method getAllResourceNames and injecting the JSON result in the mule.myLogging method
                mule.myrestx.getAllComponentNamesPlus(
                    function(data) {
                        mule.myLogging(data, 'RESTx Server Specialized Resources');
                    },
                    function(data) {
                        mule.myErrorLogging(data, 'RESTx Server');
                    }, true);
        });
        $('#components').click(function(e) {
                e.preventDefault();
                //Calling public method getAllComponentNames and injecting the JSON result in the mule.myLogging method
                mule.myrestx.getAllComponentNames(
                    function(data) {
                        mule.myLogging(data, 'RESTx Server Components');
                    },
                    function(data) {
                        mule.myErrorLogging(data, 'RESTx Server');
                    });
        });
        $('#componentsPlus').click(function(e) {
                e.preventDefault();
                //Calling public method getAllComponentNames and injecting the JSON result in the mule.myLogging method
                mule.myrestx.getAllComponentNamesPlus(
                    function(data) {
                        mule.myLogging(data, 'RESTx Server Components');
                    },
                    function(data) {
                        mule.myErrorLogging(data, 'RESTx Server');
                    });
        });
        $('#componentDetails').click(function(e) {
                //Calling public method getComponentDetails for the TwitterComponent and injecting the JSON result in the mule.myLogging method
                e.preventDefault();
                mule.myrestx.getComponentDetails('TwitterComponent',
                    function(data) {
                        mule.myLogging(data, 'Twitter Component details');
                    },
                    function(data) {
                        mule.myErrorLogging(data, 'RESTx Server');
                    });
        });
        $('#showResource').click(function(e) {
                //Calling public method getResourceDetails for the resourcename that was typed in the textfield on the left
                e.preventDefault();
                var resourceName = $(this).prev().val();
                //if(resourceName === '') alert('please enter a resourcename first');
                mule.myrestx.getResourceDetails(resourceName,
                    function(data) {
                        mule.myLogging(data, resourceName+' details');
                    },
                    function(data) {
                        mule.myErrorLogging(data, 'RESTx Server');
                    });
        });
        $('#showComponent').click(function(e) {
                //Calling public method getSpecializedResourceDetails for the specialized resourcename that was typed in the textfield on the left
                e.preventDefault();
                var componentName = $(this).prev().val();
                //if(componentName === '') alert('please enter a specialized resourcename first');
                mule.myrestx.getComponentDetails(componentName,
                    function(data) {
                        mule.myLogging(data, componentName+' details');
                    },
                    function(data) {
                        mule.myErrorLogging(data, 'RESTx Server');
                    }, false);
        });
        $('#showSpecializedComponent').click(function(e) {
                //Calling public method getSpecializedResourceDetails for the specialized resourcename that was typed in the textfield on the left
                e.preventDefault();
                var componentName = $(this).prev().val();
                //if(componentName === '') alert('please enter a specialized resourcename first');
                mule.myrestx.getComponentDetails(componentName,
                    function(data) {
                        mule.myLogging(data, componentName+' details');
                    },
                    function(data) {
                        mule.myErrorLogging(data, 'RESTx Server');
                    }, true);
        });
        $('#useResource').click(function(e) {
                //Calling public method getComponentDetails for the resourcename that was typed in the textfield on the left
                e.preventDefault();
                var resourceName = $(this).prev().prev().val();
                var serviceName = $(this).prev().val();
                //if(resourceName === '') alert('please enter a resourceName first');
                //if(serviceName === '') alert('please enter a serviceName first');
                mule.myrestx.callService(resourceName, serviceName,
                    function(data) {
                        mule.showServicecallResult(resourceName, serviceName, data);
                    },
                    function(data) {
                        mule.myErrorLogging(data, 'RESTx Server');
                    });
        });

        //Creating resources
        $('#step1').click(function(e) {
                e.preventDefault();
                mule.myrestx.getAllComponentNames(mule.showComponents);
        });
        $('#step3').click(function(e) {
                e.preventDefault();
                var component = 'TwitterComponent';
                if($("#step2").length)
                    component = $("#step2").val();
                mule.myrestx.getComponentDetails(component,
                    function(data) {
                        mule.doResourceFormBuild(component, data);
                    },
                    function(data) {
                        mule.myErrorLogging(data, 'RESTx Server');
                    });
        });
        $('#step8').click(function(e) {
                e.preventDefault();
                if($("#step7").length) {
                    var serviceName = $("#step7").val();
                    mule.myrestx.callService(mule.currentResource, serviceName, 
                        function(data) {
                            mule.showServicecallResult(serviceName, data);
                        },
                        function(data) {
                            mule.myErrorLogging(data, 'RESTx Server');
                        });
                }
        });
});
