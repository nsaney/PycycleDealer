"""Framework for writing LAN-accessible, WebSocket-based card games."""

#############
## Imports ##
#############

### Jython ###
# see: http://www.jython.org/jythonbook/en/1.0/Concurrency.html#thread-safety
# see: http://www.jython.org/archive/21/docs/jarray.html
from __future__ import with_statement
import threading as _threading
import traceback as _traceback
import jarray as _jarray
import json as _json

### Chairosoft ###
from chairosoft.util.function import consumer as _consumer
from chairosoft.util.function import function as _function
from chairosoft.jycycle_dealer import WebSocketObject as _WebSocketObject
from chairosoft.jycycle_dealer import WebSocketObjectDelegate as _WebSocketObjectDelegate

### Jetty ###
# see: http://www.eclipse.org/jetty/download.html
# see: http://download.eclipse.org/jetty/9.2.17.v20160517/apidocs/
# see: http://download.eclipse.org/jetty/stable-9/xref/
from org.eclipse.jetty.server import Handler as _Handler
from org.eclipse.jetty.server import Server as _Server
from org.eclipse.jetty.server.handler import ContextHandler as _ContextHandler
from org.eclipse.jetty.server.handler import ContextHandlerCollection as _ContextHandlerCollection
from org.eclipse.jetty.server.handler import DefaultHandler as _DefaultHandler
from org.eclipse.jetty.server.handler import ResourceHandler as _ResourceHandler
from org.eclipse.jetty.util.log import Log as _Log
from org.eclipse.jetty.websocket.api import StatusCode as _StatusCode
from org.eclipse.jetty.websocket.api import WebSocketListener as _WebSocketListener
from org.eclipse.jetty.websocket.common import ConnectionState as _ConnectionState
from org.eclipse.jetty.websocket.server import WebSocketHandler as _WebSocketHandler
from org.eclipse.jetty.websocket.servlet import WebSocketCreator as _WebSocketCreator

### Java SE ###
# see: https://docs.oracle.com/javase/8/docs/api/
from java.lang import ClassCastException as _ClassCastException
from java.lang import ClassLoader as _ClassLoader
from java.lang import Comparable as _Comparable
from java.lang import Integer as _Integer
from java.lang import NullPointerException as _NullPointerException
from java.lang import Object as _Object
from java.lang import String as _String
from java.lang import System as _System
from java.lang import Thread as _Thread
from java.lang import Throwable as _Throwable
from java.util import ArrayList as _ArrayList
from java.util import Collections as _Collections
from java.util import Date as _Date
from java.util import HashMap as _HashMap
from java.util import Scanner as _Scanner
from java.util import TreeSet as _TreeSet
from java.util.concurrent.atomic import AtomicInteger as _AtomicInteger


##########################
## Constant Definitions ##
##########################

PARAMETER_PYCYCLE_USER_NAME = "pycycleUserName"


##########################
## Function Definitions ##
##########################

def getResourceDirectoryForModuleName(moduleName):
    resourceDirectory = None
    try:
        # serving from the "content" directory embedded in the JAR file
        prefix = "content/"
        moduleNamePath = moduleName.replace(".", "/")
        resourcePath = prefix + moduleNamePath
        resourceDirectory = _ClassLoader.getSystemResource(resourcePath).toExternalForm()
    #
    except Exception as ex:
        message = "Could not get resource directory for module '" + str(moduleName) + "'. "
        message += "Caused by: \n" + repr(ex)
        raise RuntimeError(message)
    #
    return resourceDirectory
#

def getUserNameForSession(session):
    userName = None
    try:
        request = session.getUpgradeRequest()
        requestParameters = request.getParameterMap()
        userName = requestParameters.get(PARAMETER_PYCYCLE_USER_NAME).get(0)
    #
    except:
        userName = "<No Name>"
    #
    return userName
#

def removeIfPresent(collection, key):
    result = False
    try:
        result = collection.contains(key)
        if result:
            collection.remove(key)
        #
    #
    except:
        result = False
    #
    return result
#

def getConnectionState(session):
    return session.getConnection().getIOState().getConnectionState();
#

def hasRemoteEndpoint(session):
    state = getConnectionState(session)
    return state == _ConnectionState.OPEN or state == _ConnectionState.CONNECTED;
#


#######################
## Class Definitions ##
#######################

class Card:
    """A single playing card, with game information as well as front and back images."""
    
    ## Initializer
    def __init__(self, name, description, attributes, frontImage, backImage):
        self.name = name
        self.description = description
        self.attributes = attributes
        self.frontImage = frontImage
        self.backImage = backImage
    #
    
    ## Instance Methods
    def __str__(self):
        return str(self.name) + ": " + str(self.description)
    #
    
    ### TODO ###
#

class Pile:
    pass
    
    ### TODO ###
#

class Table:
    pass
    
    ### TODO ###
#

class IntBasedComparable(_Object, _Comparable):
    """A comparable object whose comparisons are based on an integer value supplied by a subclass.
       see: http://stackoverflow.com/questions/230585/hashset-problem-equals-and-hashcode-with-contains-working-differently-than-i
    """
    
    ## Instance Methods
    def getIntValue(self):
        """Abstract Method: Returns the integer value this object will use for comparisons and equality checking."""
        raise NotImplementedError
    #
    
    def compareTo(self, other):
        if other is None:
            raise _NullPointerException()
        #
        
        selfIntValue = self.getIntValue()
        otherIntValue = None
        try:
            otherIntValue = other.getIntValue()
        #
        except:
            raise _ClassCastException()
        #
        
        return _Integer.compare(selfIntValue, otherIntValue)
    #
    
    def equals(self, other):
        try:
            selfIntValue = self.getIntValue()
            otherIntValue = other.getIntValue()
            return _Integer.equals(selfIntValue, otherIntValue)
        #
        except:
            return False
        #
    #
    
    def __eq__(self, other):
        return self.equals(other)
    #
    
    def hashCode(self):
        selfIntValue = self.getIntValue()
        return _Integer.hashCode(selfIntValue)
    #
    
    def __hash__(self):
        return self.hashCode()
    #
#

class User(IntBasedComparable):
    """A user in a game room, who may be the room's host, and who may be a player or simply a spectator.
       Each user has a ticket number that can be used to uniquely identify and order them.
    """
    
    ## Initializer
    def __init__(self, ticketNumber, session):
        self.ticketNumber = ticketNumber
        self.session = session
        self.name = getUserNameForSession(session)
    #
    
    ## Instance Methods
    def getIntValue(self):
        """Required method for IntBasedComparable."""
        return self.ticketNumber
    #
    
    def asDictionary(self):
        return {"name": self.name, "ticketNumber": self.ticketNumber}
    #
    
    def __str__(self):
        return 'User "%s" (Ticket #%d)' % (self.name, self.ticketNumber)
    #
    
    def __repr__(self):
        return '%r{name="%s",ticketNumber=%s}' % (type(self), self.name, self.ticketNumber)
    #
#

class UserAction:
    ## Static Fields
    PARSE_ERROR = "__error__"
    
    ## Initializer
    def __init__(self, text):
        self.parseSuccess = False
        self.originalJsonText = text
        try:
            jsonObject = _json.loads(text)
            self.target = jsonObject["target"]
            self.method = jsonObject["method"]
            self.parameters = jsonObject["parameters"]
            if not isinstance(self.parameters, dict):
                raise Exception
            #
            self.parseSuccess = True
        #
        except:
            self.target = UserAction.PARSE_ERROR
            self.method = UserAction.PARSE_ERROR
            self.parameters = {}
        #
    #
#

class UserInterfaceUpdate:
    ## Initializer
    def __init__(self, target, method, parameters):
        self.originalTarget = target
        self.originalMethod = method
        self.originalParameters = parameters
        self.jsonText = _json.dumps({"target": target, "method": method, "parameters": parameters})
    #
#

class Game:
    """A card game to be played in a Room.
       Extend this class to define a new card game.
    """
    
    ## Instance Methods
    def getResourceDirectory(self):
        return getResourceDirectoryForModuleName(self.__module__)
    #
    
    ### TODO ###
#

class Room:
    """A room for chatting and playing games."""
    
    ## Static Fields
    INITIAL_TICKET_NUMBER = 1
    DEFAULT_MAX_USER_COUNT = 32
    
    ## Initializer
    def __init__(self, gameList):
        self.LOG = _Log.getLogger(type(self))
        self.name = "New Room"
        self.host = None
        self.playerList = []
        self.gameList = gameList
        self.currentGame = None
        
        self.nextTicketNumber = _AtomicInteger(Room.INITIAL_TICKET_NUMBER)
        self.maxUserCount = Room.DEFAULT_MAX_USER_COUNT
        self.waitingUsersSortedSet = _TreeSet()
        self.activeUsersSortedSet = _TreeSet()
        self.usersBySession = _HashMap()
        self.usersByTicketNumber = _HashMap()
        self.usersLock = _threading.RLock() # reentrant lock
        self.ensuringHostLock = _threading.Lock() # non-reentrant lock
        
        self.actionDictionary = self.getActionDictionary()
    #
    
    ## Instance Methods - User Management
    def getNextTicketNumber(self):
        return self.nextTicketNumber.getAndIncrement()
    #
    
    def getFirstWaitingUserOrNone(self):
        result = None
        with self.usersLock:
            if self.waitingUsersSortedSet.size() > 0:
                result = self.waitingUsersSortedSet.first()
            #
        #
        return result
    #
    
    def getFirstActiveUserOrNone(self):
        result = None
        with self.usersLock:
            if self.activeUsersSortedSet.size() > 0:
                result = self.activeUsersSortedSet.first()
            #
        #
        return result
    #
    
    def getTotalUserCount(self):
        """Includes users in the waiting room as well as active users.
           Note that this is unreliable unless the calling thread already holds the lock!
        """
        result = self.maxUserCount + 1
        with self.usersLock:
            waitingUserCount = self.waitingUsersSortedSet.size() 
            activeUserCount = self.activeUsersSortedSet.size()
            result = waitingUserCount + activeUserCount
        #
        return result
    #
    
    def getUserForSession(self, session):
        result = None
        with self.usersLock:
            result = self.usersBySession.get(session)
        #
        return result
    #
    
    def getUserForTicketNumber(self, ticketNumber):
        result = None
        with self.usersLock:
            result = self.usersByTicketNumber.get(ticketNumber)
        #
        return result
    #
    
    def addSessionToWaitingSet(self, session):
        success = False
        with self.usersLock:
            totalUserCount = self.getTotalUserCount()
            tooManyUsers = totalUserCount >= self.maxUserCount
            isWaiting = self.waitingUsersSortedSet.stream() \
                .anyMatch(_function(lambda waitingUser: waitingUser.session is session))
            if not tooManyUsers and not isWaiting:
                ticketNumber = self.getNextTicketNumber()
                user = User(ticketNumber, session)
                self.waitingUsersSortedSet.add(user)
                self.usersBySession.put(user.session, user)
                self.usersByTicketNumber.put(user.ticketNumber, user)
                success = True
            #
            else:
                if session.isOpen():
                    reason = "Too many users." if tooManyUsers else "Session is already waiting."
                    session.close(_StatusCode.NORMAL, reason)
                #
            #
            
            # log event
            if success:
                self.LOG.info("Successfully added %s (session %s) to the waiting set." % (user, user.session.hashCode()))
            #
            else:
                self.LOG.info("Could not add %s (session %s) to the waiting set (tooManyUsers=%s, isWaiting=%s)." % (user, session.hashCode(), tooManyUsers, isWaiting))
            #
            
            # followup
            if success:
                self.ensureHostExistsAndUpdateRoom()
            #
        #
        return success
    #
    
    def moveUserToActiveSet(self, user):
        success = False
        with self.usersLock:
            isWaiting = self.waitingUsersSortedSet.contains(user)
            isActive = self.activeUsersSortedSet.contains(user)
            if isWaiting and not isActive:
                self.waitingUsersSortedSet.remove(user)
                self.activeUsersSortedSet.add(user)
                self.sendUserActivation(user)
                success = True
            #
        
            # log event
            if success:
                self.LOG.info("Successfully moved %s to the active set." % (user))
            #
            else:
                self.LOG.info("Could not move %s to the active set (isWaiting=%s, isActive=%s)." % (user, isWaiting, isActive))
            #
            
            # followup
            if success:
                self.ensureHostExistsAndUpdateRoom()
            #
        #
        return success
    #
    
    def removeUserForSession(self, session, reason):
        success = False
        with self.usersLock:
            user = self.getUserForSession(session)
            success = self.removeUser(user, reason)
        #
        return success
    #
    
    def removeUser(self, user, reason):
        success = False
        with self.usersLock:
            waitingRemovalSuccess = removeIfPresent(self.waitingUsersSortedSet, user)
            activeRemovalSuccess = removeIfPresent(self.activeUsersSortedSet, user)
            success = waitingRemovalSuccess or activeRemovalSuccess
            
            if success:
                if user.session.isOpen():
                    user.session.close(_StatusCode.NORMAL, reason)
                #
                
                removeIfPresent(self.usersBySession, user.session)
                removeIfPresent(self.usersByTicketNumber, user.ticketNumber)
            #
        
            # log event
            if success:
                self.LOG.info("Successfully removed %s from the room for reason '%s'." % (user, reason))
            #
            else:
                self.LOG.info("Unable to find %s in room to remove for reason '%s'." % (user, reason))
            #
            
            # followup
            if success:
                if user is self.host:
                    self.host = None
                #
                self.ensureHostExistsAndUpdateRoom()
            #
        #
        return success
    #
    
    def ensureHostExistsAndUpdateRoom(self):
        success = False
        with self.usersLock:
            if self.ensuringHostLock.locked():
                return False
            #
            with self.ensuringHostLock:
                if self.host is None:
                    # choose first-in-line active user
                    firstActiveUser = self.getFirstActiveUserOrNone()
                    if firstActiveUser is None:
                        # if no active users, activate first-in-line waiting user
                        firstWaitingUser = self.getFirstWaitingUserOrNone()
                        if firstWaitingUser is not None:
                            self.moveUserToActiveSet(firstWaitingUser)
                            firstActiveUser = firstWaitingUser
                        #
                    #
                    
                    if firstActiveUser is not None:
                        self.sendHostChange(firstActiveUser)
                    #
                #
                
                success = self.host is not None
                if success:
                    self.sendUserSetsToHost()
                #
                else:
                    self.LOG.info("All users have left the room, so there is no host.")
                #
            #
        #
        return success
    #
    
    def ensureUserIsHost(self, user):
        if self.host is not user:
            raise RuntimeError("User %s is not the host." % (user))
        #
    #
    
    
    ## Instance Methods - Receiving from Clients
    def handleSessionAction(self, session, text):
        with self.usersLock:
            user = self.getUserForSession(session)
            userAction = UserAction(text)
            
            actionMethod = None
            if userAction.target in self.actionDictionary:
                targetDictionary = self.actionDictionary[userAction.target]
                if userAction.method in targetDictionary:
                    actionMethod = targetDictionary[userAction.method]
                #
            #
            
            success = False
            errorMessage = ""
            if hasattr(actionMethod, "__call__"):
                try:
                    actionMethod(user, userAction.parameters)
                    success = True
                #
                except Exception as ex:
                    errorMessage = repr(ex)
                    #_traceback.print_exc()
                #
            #
            else:
                errorMessage = "No dictionary entry for handling user action."
            #
            self.sendAcknowledge(user, userAction, success, errorMessage)
        #
    #
    
    def handle_room_clientExit(self, user, actionParameters):
        with self.usersLock:
            if user.session.isOpen():
                statusCode = _StatusCode.NORMAL
                reason = "Client Exit: " + actionParameters["reason"]
                user.session.close(statusCode, reason);
            #
        #
    #
    
    def handle_room_chat(self, user, actionParameters):
        message = actionParameters["message"]
        self.sendChatMessage(user, message)
    #
    
    def handle_room_activateTicketNumber(self, user, actionParameters):
        with self.usersLock:
            self.ensureUserIsHost(user)
            ticketNumber = actionParameters["ticketNumber"]
            userToActivate = self.getUserForTicketNumber(ticketNumber)
            self.moveUserToActiveSet(userToActivate)
        #
    #
    
    def handle_room_removeTicketNumber(self, user, actionParameters):
        with self.usersLock:
            self.ensureUserIsHost(user)
            ticketNumber = actionParameters["ticketNumber"]
            userToRemove = self.getUserForTicketNumber(ticketNumber)
            reason = actionParameters["reason"]
            self.removeUser(userToRemove, reason)
        #
    #
    
    def getActionDictionary(self):
        return {
            "room": {
                "clientExit": self.handle_room_clientExit,
                "chat": self.handle_room_chat,
                "activateTicketNumber": self.handle_room_activateTicketNumber,
                "removeTicketNumber": self.handle_room_removeTicketNumber,
                "_startGame": None
            },
            "_game": {
            }
        }
    #
    
    
    ## Instance Methods - Sending to Clients
    def sendInterfaceUpdateToUser(self, userInterfaceUpdate, user):
        try:
            if hasRemoteEndpoint(user.session):
                remote = user.session.getRemote()
                remote.sendString(userInterfaceUpdate.jsonText)
            #
        #
        except _Throwable as ex:
            message = "Problem while sending update to %s. " % (user)
            message += "Session hasRemoteEndpoint=%s. " % (hasRemoteEndpoint(user.session))
            message += "Cxn state=%s. " % (getConnectionState(user.session))
            message += "Error: %r" % (ex)
            self.LOG.warn(message)
        #
    #
    
    def sendInterfaceUpdateToSession(self, userInterfaceUpdate, session):
        user = self.getUserForSession(session)
        self.sendInterfaceUpdateToUser(user)
    #
    
    def sendInterfaceUpdateToAllActive(self, userInterfaceUpdate):
        with self.usersLock:
            for user in self.activeUsersSortedSet.iterator():
                self.sendInterfaceUpdateToUser(userInterfaceUpdate, user)
            #
        #
    #
    
    def sendAcknowledge(self, user, userAction, success, errorMessage):
        if not success:
            message = "Error occurred while handling action from %s: %s \nOriginal action: %s" % (user, errorMessage, userAction.originalJsonText)
            self.LOG.warn(message)
        #
        
        userInterfaceUpdate = UserInterfaceUpdate(
            target = "room",
            method = "acknowledge",
            parameters = {
                "originalJsonText": userAction.originalJsonText,
                "parseSuccess": userAction.parseSuccess,
                "success": success,
                "errorMessage": errorMessage
            }
        );
        self.sendInterfaceUpdateToUser(userInterfaceUpdate, user)
    #
    
    def sendUserActivation(self, activatedUser):
        with self.usersLock:
            userInterfaceUpdate = UserInterfaceUpdate(
                target = "room", 
                method = "activate", 
                parameters = {}
            )
            self.sendInterfaceUpdateToUser(userInterfaceUpdate, activatedUser)
        #
    #
    
    def sendHostChange(self, nextHost):
        with self.usersLock:
            oldHost = self.host
            self.host = nextHost
            self.LOG.info("Changed the host of the room from %s to %s." % (oldHost, self.host))
            
            hostDeactivate = UserInterfaceUpdate(
                target = "room", 
                method = "hostDeactivate", 
                parameters = {}
            )
            self.sendInterfaceUpdateToAllActive(hostDeactivate)
            
            hostActivate = UserInterfaceUpdate(
                target = "room",
                method = "hostActivate",
                parameters = {}
            )
            self.sendInterfaceUpdateToUser(hostActivate, nextHost)
        #
    #
    
    def sendUserSetsToHost(self):
        with self.usersLock:
            waitingUsersList = map(lambda u: u.asDictionary(), self.waitingUsersSortedSet.iterator())
            #waitingUsersList = self.waitingUsersSortedSet.stream() \
            #    .map(_function())
            activeUsersList = map(lambda u: u.asDictionary(), self.activeUsersSortedSet.iterator())
            #activeUsersList = self.activeUsersSortedSet.stream() \
            #    .map(_function(lambda u: u.asDictionary()))
            userInterfaceUpdate = UserInterfaceUpdate(
                target = "room",
                method = "hostUserSets",
                parameters = {
                    "waitingUsersList": waitingUsersList,
                    "activeUsersList": activeUsersList
                }
            )
            self.sendInterfaceUpdateToUser(userInterfaceUpdate, self.host)
        #
    #
    
    def sendChatMessage(self, user, message):
        with self.usersLock:
            if not self.activeUsersSortedSet.contains(user):
                return
            #
            userInterfaceUpdate = UserInterfaceUpdate(
                target = "room",
                method = "chat",
                parameters = {
                    "serverEpochTimestampMs": _Date().getTime(),
                    "userName": user.name,
                    "message": message
                }
            )
            self.sendInterfaceUpdateToAllActive(userInterfaceUpdate)
        #
    #
#

class RoomWebSocketDelegate(_WebSocketObjectDelegate):
    ## Initializer
    def __init__(self, room):
        self.room = room
    #
    
    ## Instance Methods
    def handleWebSocketConnect(self, session):
        session.setIdleTimeout(-1)
        self.room.LOG.info("New session: " + str(session.hashCode()))
        self.room.addSessionToWaitingSet(session)
    #
    
    def handleWebSocketMessageString(self, session, text):
        self.room.handleSessionAction(session, text)
    #
    
    def handleWebSocketError(self, session, error):
        user = self.room.getUserForSession(session)
        self.room.LOG.warn("There was a WebSocket error with %s." % (user))
    #
    
    def handleWebSocketClose(self, session, statusCode, reason):
        self.room.removeUserForSession(session, reason)
    #
#

class RoomWebSocketCreator(_WebSocketCreator):
    ## Initializer
    def __init__(self, room):
        roomWebSocketDelegate = RoomWebSocketDelegate(room)
        self.webSocketObject = _WebSocketObject(roomWebSocketDelegate)
    #
    
    ## Instance Methods
    def createWebSocket(self, req, resp):
        # Always accept the first sub protocol, if available
        requestedSubProtocols = req.getSubProtocols()
        if requestedSubProtocols.size() > 0:
            acceptedSubProtocol = requestedSubProtocols.get(0)
            resp.setAcceptedSubProtocol(acceptedSubProtocol)
        #
        
        # Always return the same web socket object on each request
        return self.webSocketObject
    #
#

class RoomWebSocketHandler(_WebSocketHandler):
    ## Initializer
    def __init__(self, game):
        self.roomWebSocketCreator = RoomWebSocketCreator(game)
    #
    
    ## Instance Methods
    def configure(self, factory):
        factory.setCreator(self.roomWebSocketCreator)
    #
#

class RoomServer:
    """A server that backs a Room."""
    
    ## Initializer
    def __init__(self, port):
        # from init args
        self.port = port
        self.room = Room([])
        self.webServer = None
    #
    
    ## Instance Methods
    def start(self):
        # see: http://www.eclipse.org/jetty/documentation/current/embedding-jetty.html
        self.webServer = _Server(self.port)
        
        rootHandler = _ContextHandlerCollection()
        childHandlers = _ArrayList()
        
        ## Web Sockets
        websocketContext = _ContextHandler(rootHandler, "/websocket")
        websocketContext.setAllowNullPathInfo(True) # so "/abc" is not redirected to "/abc/"
        websocketHandler = RoomWebSocketHandler(self.room)
        websocketContext.setHandler(websocketHandler)
        childHandlers.add(websocketContext)
        
        ## Files
        resourceContext = _ContextHandler(rootHandler, "/")
        resourceHandler = _ResourceHandler()
        resourceHandler.setDirectoriesListed(True)
        resourceHandler.setWelcomeFiles(_jarray.array(["index.html"], _String))
        resourceDirectory = getResourceDirectoryForModuleName(__name__)
        resourceHandler.setResourceBase(resourceDirectory)
        resourceContext.setHandler(resourceHandler)
        resourceContext.setLogger(_Log.getLogger(_ResourceHandler))
        childHandlers.add(resourceContext)
        
        ## DefaultHandler
        childHandlers.add(_DefaultHandler())
        
        rootHandler.setHandlers(_jarray.array(childHandlers, _Handler))
        self.webServer.setHandler(rootHandler)
        
        self.webServer.start()
        self.webServer.join()
    #
    
    def stop(self):
        self.webServer.stop()
    #
#

#################
## End of File ##
#################

