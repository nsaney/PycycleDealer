// Nicholas Saney
// 
// Created: August 10, 2016
// 
// utils.js
// This file has miscellaneous JS definitions


////////////////////
// Error Catching //
////////////////////

(function () {
    // just in case
    if (!window.console) {
        window.console = {
            log: function () {}
        };
    }
    
    // last resort error catcher
    window.lastError = null;
    function window_onerror(message, source, line, col, error) {
        console.log("Error in " + source + " at line #" + line + ", col=" + col + ": " + message)
        window.lastError = error;
    }
    window.addEventListener('error', window_onerror, false);
});


///////////////////////
// Utility Functions //
///////////////////////

(function () {
    if (window.utils) { return console.log('Property window.utils already exists!'); }
    var utils = window.utils = {};
    
    // see: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/encodeURIComponent
    utils.fixedEncodeURIComponent = function (str) {
      return encodeURIComponent(str).replace(/[!'()*]/g, function(c) {
        return '%' + c.charCodeAt(0).toString(16);
      });
    };
    
    utils.padLeft = function (str, ch, len) {
        str = '' + str;
        while (str.length < len) { str = ch + str; }
        return str;
    };
    
    utils.sendJson = function (websocket, object) {
        if (websocket && websocket.readyState === WebSocket.OPEN) {
            var jsonText = JSON.stringify(object);
            websocket.send(jsonText);
        }
    };
})();


///////////////////////
// Knockout Bindings //
///////////////////////
// see: http://knockoutjs.com/documentation/custom-bindings.html
(function () { 
    if (!$ || !window.utils || !window.ko || !ko.bindingHandlers) { return console.log('Did not try to create utils.ko_bindingHandlers property.'); }
    if (utils.ko_bindingHandlers) { return console.log('Property utils.ko_bindingHandlers already exists!'); }
    utils.ko_bindingHandlers = {};
    
    // Note: both init and update take the following parameters.
    // function(element, valueAccessor, allBindings, viewModel, bindingContext) {}
    
    utils.ko_bindingHandlers.chatDateFromTimeMs = {
        update: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
            var timeMsValue = ko.unwrap(valueAccessor());
            var dateValue = new Date(timeMsValue);
            
            // date part
            var year = dateValue.getFullYear();
            var month = dateValue.getMonth() + 1;
            var day = dateValue.getDate();
            var datePart = [year, month, day].map(str => utils.padLeft(str, '0', 2)).join('-');
            
            // time part
            var hour = dateValue.getHours();
            var minute = dateValue.getMinutes();
            var second = dateValue.getSeconds();
            var timePart = [hour, minute, second].map(str => utils.padLeft(str, '0', 2)).join(':');
            
            // full text
            var dateText = datePart + ' ' + timePart;
            element.textContent = dateText;
        }
    };
    
    // apply to ko.bindingHandlers
    $.extend(ko.bindingHandlers, utils.ko_bindingHandlers);
})();
