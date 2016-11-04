// Nicholas Saney
// 
// Created: August 10, 2016
// 
// index.js
// Index page viewmodel

var websocket = null;
function window_onbeforeunload(e) {
    utils.sendJson(websocket, {
        target: 'room',
        method: 'clientExit',
        parameters: {
            reason: 'window.onbeforeunload'
        }
    });
}
window.addEventListener('beforeunload', window_onbeforeunload, false);

var windowLoaded = ko.observable(false);
function window_onload(e) {
    windowLoaded(true);
}
window.addEventListener('load', window_onload, false);

ko.applyBindings(new (function IndexViewModel() {
    
    var self = this;
    
    // KO Observable Properties
    self.websocketReadyState = ko.observable();
    self.websocketErrorText = ko.observable();
    self.websocketCloseText = ko.observable();
    self.userName = ko.observable();
    self.ticketNumber = ko.observable();
    self.isHost = ko.observable(false);
    self.waitingUsersList = ko.observableArray([]);
    self.activeUsersList = ko.observableArray([]);
    self.chatWorkingMessage = ko.observable('');
    self.chatEntries = ko.observableArray([
    /*
        {
            serverEpochTimestampMs: Date.now(),
            user: { name: 'Test 1', ticketNumber: 1 },
            message: 'Test 1 message'
        },
        {
            serverEpochTimestampMs: Date.now(),
            user: { name: 'Test 2', ticketNumber: 2, isMe: true },
            message: 'Test 2 message'
        },
        {
            serverEpochTimestampMs: Date.now(),
            user: { name: 'Test 3', ticketNumber: 3 },
            message: 'Test 3 message'
        },
    */
    ]);
    self.chatIsScrolled = ko.observable(false);
    self.game = ko.observable();
    self.chatEntriesComputedFlexStyles = ko.computed(function () {
        if (!windowLoaded()) { return []; }
        var regex = /(flex|overflow)/;
        var divChatEntries = document.getElementById('divChatEntries');
        if (!divChatEntries) { return []; }
        var divChatEntriesStyles = window.getComputedStyle(divChatEntries, null);
        var result = [];
        for (var i = 0; i < divChatEntriesStyles.length; ++i) {
            var name = divChatEntriesStyles[i];
            var value = divChatEntriesStyles.getPropertyValue(name);
            if (regex.test(name) || regex.test(value)) {
                result.push({ name: name, value: value });
            }
        }
        return result;
    });
    
    
    // Web Socket Handler
    // see: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_client_applications
    self.formEnterRoom_onsubmit = function () {
        var loc = window.location;
        var websocketProtocol = loc.protocol === 'https:' ? 'wss:' : 'ws:';
        var websocketUri = websocketProtocol + loc.host + '/websocket';
        websocketUri += '?pycycleUserName=' + utils.fixedEncodeURIComponent(self.userName());
        var websocketSubProtocols = [];
        websocket = new WebSocket(websocketUri, websocketSubProtocols);
        websocket.onopen = onWebSocketOpen;
        websocket.onmessage = onWebSocketMessage;
        websocket.onerror = onWebSocketError;
        websocket.onclose = onWebSocketClose;
        self.websocketReadyState(websocket.readyState);
    };
    
    function onWebSocketOpen(event) {
        self.websocketReadyState(websocket.readyState);
    };
    
    function onWebSocketMessage(event) {
        self.websocketReadyState(websocket.readyState);
        var update = JSON.parse(event.data);
        handleUpdate(update);
    };
    
    function onWebSocketError(event) {
        self.websocketReadyState(websocket.readyState);
        self.websocketErrorText('Problem with WebSocket: ' + event);
        console.log(event);
    };
    
    function onWebSocketClose(event) {
        self.websocketReadyState(websocket.readyState);
        self.websocketCloseText('WebSocket closed with code ' + event.code + ' and reason "' + event.reason + '"');
        console.log(event);
    };
    
    
    // Receiving from Server
    function handleUpdate(update) {
        var updateFunction = null;
        var targetDictionary = updateDictionary[update.target];
        if (targetDictionary) {
            updateFunction = targetDictionary[update.method];
        }
        
        if (typeof updateFunction === 'function') {
            try {
                updateFunction(update.parameters);
            }
            catch (err) {
                var message = 'Error occurred while handling update: ' + err;
                console.log(message);
            }
        }
        else {
            console.log('Unable to handle update: ' + event.data);
        }
    }
    
    var acknowledgeDictionary = {
        // this becomes fully populated later, in "Sending to Server" section
        room: {},
        game: {}
    }; 
    function room_acknowledge(updateParameters) {
        var originalJsonText = updateParameters.originalJsonText;
        var parseSuccess = updateParameters.parseSuccess;
        if (parseSuccess) {
            var originalAction = JSON.parse(originalJsonText);
            var success = updateParameters.success;
            if (success) {
                var acknowledgeFunction = null;
                var targetDictionary = acknowledgeDictionary[originalAction.target];
                if (targetDictionary) {
                    acknowledgeFunction = targetDictionary[originalAction.method];
                }
                
                if (typeof acknowledgeFunction === 'function') {
                    try {
                        acknowledgeFunction(originalAction);
                    }
                    catch (err) {
                        var message = 'Error occurred while handling acknowledgment: ' + err;
                        console.log(message);
                    }
                }
                else {
                    // no acknowledge function
                }
            }
            else {
                var errorMessage = updateParameters.errorMessage;
                console.log("Server error while handling action: " + errorMessage + "\nFrom " + originalJsonText)
            }
        }
        else {
            console.log("Server could not parse action: " + originalJsonText);
        }
    };
    
    function room_activate(updateParameters) {
        self.userName(updateParameters.user.name);
        self.ticketNumber(updateParameters.user.ticketNumber);
    };
    
    function room_hostActivate(updateParameters) {
        self.isHost(true);
    };
    
    function room_hostDeactivate(updateParameters) {
        self.isHost(false);
        self.waitingUsersList([]);
        self.activeUsersList([]);
    };
    
    function room_hostUserSets(updateParameters) {
        self.waitingUsersList(updateParameters.waitingUsersList);
        self.activeUsersList(updateParameters.activeUsersList);
    };
    
    function room_chat(updateParameters) {
        updateParameters.user.isMe = (updateParameters.user.ticketNumber === self.ticketNumber());
        var startedScrolled = self.chatIsScrolled();
        self.chatEntries.push(updateParameters);
        if (!startedScrolled) {
            var $divChatEntries = $('#divChatEntries');
            $divChatEntries.animate({ scrollTop: $divChatEntries[0].scrollHeight }, 500);
        }
    };
    self.divChatEntries_onscroll = function (data, event) {
        // see: https://developer.mozilla.org/en-US/docs/Web/API/Element/scrollHeight#Determine_if_an_element_has_been_totally_scrolled
        var element = event.target;
        var isScrolled = (element.scrollHeight - element.scrollTop !== element.clientHeight);
        self.chatIsScrolled(isScrolled);
    };
    
    var updateDictionary = {
        'room': {
            'acknowledge': room_acknowledge,
            'activate': room_activate,
            'hostActivate': room_hostActivate,
            'hostDeactivate': room_hostDeactivate,
            'hostUserSets': room_hostUserSets,
            'chat': room_chat
        },
        '_game': {
        }
    };
    
    
    // Sending to Server (and handling acknowledgment receipts)
    self.formChat_onsubmit = function () {
        var message = self.chatWorkingMessage();
        self.chatWorkingMessage('');
        sendChatMessage(message);
    };
    function sendChatMessage(chatMessage) {
        utils.sendJson(websocket, {
            target: 'room',
            method: 'chat',
            parameters: {
                message: chatMessage
            }
        });
    };
    
    self.activateUser = function (user) {
        sendActivateTicketNumber(user.ticketNumber);
    };
    function sendActivateTicketNumber(ticketNumber) {
        utils.sendJson(websocket, {
            target: 'room',
            method: 'activateTicketNumber',
            parameters: {
                ticketNumber: ticketNumber,
            }
        });
    };
    acknowledgeDictionary.room.activateTicketNumber = function (originalAction) {
        var ticketNumber = originalAction.parameters.ticketNumber;
        var message = 'Successfully activated ticket number #' + ticketNumber;
        console.log(message);
    };
    
    self.makeHostUser = function (user) {
        sendMakeHostTicketNumber(user.ticketNumber);
    };
    function sendMakeHostTicketNumber(ticketNumber) {
        utils.sendJson(websocket, {
            target: 'room',
            method: 'makeHostTicketNumber',
            parameters: {
                ticketNumber: ticketNumber,
            }
        });
    };
    acknowledgeDictionary.room.makeHostTicketNumber = function (originalAction) {
        var ticketNumber = originalAction.parameters.ticketNumber;
        var message = 'Successfully made ticket number #' + ticketNumber + ' host';
        console.log(message);
    };
    
    self.removeUser = function (user) {
        sendRemoveTicketNumber(user.ticketNumber, 'Removed by Host');
    };
    function sendRemoveTicketNumber(ticketNumber, reason) {
        utils.sendJson(websocket, {
            target: 'room',
            method: 'removeTicketNumber',
            parameters: {
                ticketNumber: ticketNumber,
                reason: reason
            }
        });
    };
    acknowledgeDictionary.room.removeTicketNumber = function (originalAction) {
        var ticketNumber = originalAction.parameters.ticketNumber;
        var message = 'Successfully removed ticket number #' + ticketNumber;
        console.log(message);
    };
})());