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
    self.chatEntries = ko.observableArray([]);
    self.game = ko.observable();
    
    
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
        var serverTimestamp = new Date(updateParameters.serverEpochTimestampMs);
        self.chatEntries.push(updateParameters);
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