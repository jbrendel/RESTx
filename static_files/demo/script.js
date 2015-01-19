
String.prototype.startsWith = function(str) 
{return (this.match("^"+str)==str)}

String.prototype.endsWith = function(str) 
{return (this.match(str+"$")==str)}

var interval_id     = null;
var elems           = new Array();
var elems_bg_color  = new Array();
var elems_color     = new Array();
var blink_interval  = 250;

Array.prototype.has = function(v) {
    var ind;
    for (ind=0; ind<this.length; ind++) {
        if (this[ind]==v) return true;
    }
    return false;
}

function ScrollToElement(theElement){
    // Code for this function is from: http://radio.javaranch.com/pascarello/2005/01/09/1105293729000.html
    // with some additions and modifications to prevent unnecessary scrolling (if the element is already
    // in view).
    var selectedPosX = 0;
    var selectedPosY = 0;

    while(theElement != null) {
        selectedPosX += theElement.offsetLeft;
        selectedPosY += theElement.offsetTop;
        theElement = theElement.offsetParent;
    }
    var current_scroll_offset = parent.top.frames[2].pageYOffset;
    if (top.frames[2].innerHeight + current_scroll_offset < selectedPosY  ||  selectedPosY < current_scroll_offset) {
        parent.top.frames[2].scrollTo(selectedPosX,selectedPosY);
    }
}

function linkHigh(lname)
{
    if (lname in elems) {
        link = elems[lname];
        if (!(lname in elems_bg_color)) {
            elems_bg_color[lname] = link.style.backgroundColor;
            elems_color[lname]    = link.style.color;
        }
        link.style.backgroundColor="#ff0000";
        link.style.color="#ffffff";
        setTimeout("linkLow('" + lname + "')", blink_interval);
    }
}

function linkLow(lname, no_high)
{
    if (lname in elems) {
        link = elems[lname];
        link.style.backgroundColor = elems_bg_color[lname];
        link.style.color           = elems_color[lname];
        if (no_high === undefined) {
            setTimeout("linkHigh('" + lname + "')", blink_interval);
        }
    }
}

function getLinkByUrl(url)
{
    var search_start = false;
    if (url.endsWith("###")) {
        url = url.substring(0, url.length-3);
        search_start = true;
    }
    var doc = parent.top.frames[2].document;
    var links = doc.getElementsByTagName("A");
    var total = links.length
    for (i=0; i<total; i++) {
        if ((!search_start  &&  (links[i].innerHTML == url))  ||  (search_start && links[i].innerHTML.startsWith(url))) {
            ScrollToElement(links[i]);
            return links[i];
        }
    }
    return null;
}

function linkHighlight(url)
{
    var link = getLinkByUrl(url);
    if (link != null) {
        elems[link.innerHTML] = link;
        linkHigh(link.innerHTML);
    }
}

function stopLinkHighlight(url)
{
    var link = getLinkByUrl(url);
    if (link != null) {
        var link_name = link.innerHTML;
        if (link_name in elems) {
            linkLow(link_name, true);
            delete elems[link_name];
        }
    }
}

function getElemById(id)
{
    var doc  = parent.top.frames[2].document;
    var elem = doc.getElementById(id);
    return elem;
}

function elemHighlight(id)
{
    var elem = getElemById(id);
    if (elem != null) {
        elems[id] = elem;
        ScrollToElement(elem);
        elemHigh(id);
    }
}

function rowHighlight(id)
{
    elemHighlight(id+"_name");
    //elemHighlight(id+"_value");
}

function elemHigh(id)
{
    if (id in elems) {
        var elem = elems[id];
        if (!(id in elems_bg_color)) {
            elems_bg_color[id] = elem.style.backgroundColor;
        }
        elem.style.backgroundColor="#ff8888";
    }
}

function elemLow(id, no_high)
{
    var id;
    if (id in elems) {
        var elem = elems[id];
        elem.style.backgroundColor = elems_bg_color[id];
        if (no_high === undefined) {
            setTimeout("elemHigh('" + id + "')", blink_interval);
        }
    }
}

function stopElemHighlight(id)
{
    var elem = getElemById(id);
    if (elem != null  &&  id in elems) {
        elemLow(id, true);
        delete elems[id];
        if (id in elems_bg_color) {
            delete elems_bg_color[id];
        }
        if (id in elems_color) {
            delete elems_color[id];
        }
    }
}

function stopRowHighlight(id)
{
    stopElemHighlight(id+"_name");
    //stopElemHighlight(id+"_value");
}

function onClickActionLink()
{
    alert("Sorry, but this link is not part of the demo...");
    return false;
}

function onClickActionCheckbox()
{
    alert("Sorry, but checking this element is currently disabled for the demo.");
    return false;
}

function disableLinks(url_list)
{
    // First get all the links that should NOT be disable
    var allowed_links = new Array();
    var i;
    for (i=0; i<url_list.length; ++i) {
        allowed_links.push(getLinkByUrl(url_list[i]));
    }

    var doc   = parent.top.frames[2].document;
    var links = doc.getElementsByTagName("a");
    for (i=0; i<links.length; ++i) {
        if (!allowed_links.has(links[i])) {
            links[i].onclick = onClickActionLink;
        }
    }
}

function disableClickById(id)
{
    var doc   = parent.top.frames[2].document;
    var elem  = doc.getElementById(id);
    elem.onclick = onClickActionCheckbox;
    elem.checked = false;
}

function forceFieldValue(id, value, title, ignore_case)
{
    var doc  = parent.top.frames[2].document;
    var elem = doc.getElementsByName(id)[0];
    elem.onchange = function() {
                        var ev = elem.value;
                        var v  = value;
                        if (ignore_case) {
                            ev = ev.toLowerCase();
                            v  = v.toLowerCase();
                        }
                        if (ev != v) {
                            alert("Sorry, but for the demo, please enter exactly '" + value + "' for the '" + title + "' field.");
                            elem.value = "";
                            elem.focus();
                            return false;
                        }
                    }
}

function forceEmptyFieldValue(id)
{
    var doc  = parent.top.frames[2].document;
    var elem = doc.getElementsByName(id)[0];
    elem.onchange = function() {
                        if (elem.value.length > 0) {
                            alert("Sorry, but for the demo, please leave this field empty.");
                            elem.value = "";
                            return false;
                        }
                    }
}
   

function changeInnerHtml(id, value)
{
    var doc  = parent.top.frames[2].document;
    var elem = doc.getElementById(id);
    elem.innerHTML = value;
}

/*
 * Create the menu at the top
 */

function makeMenu()
{
    var elem = document.getElementById("menu_div");
    elem.innerHTML = " \
<a href=\"/static/demo/demo.html\" target=\"_top\">Restart demo</a> &nbsp; - &nbsp; \
<a href=\"http://restx.mulesoft.org\" target=\"_blank\">RESTx home page</a> &nbsp; - &nbsp; \
<a href=\"http://restx.mulesoft.org/download-restx\" target=\"_blank\">Download</a>";
}

