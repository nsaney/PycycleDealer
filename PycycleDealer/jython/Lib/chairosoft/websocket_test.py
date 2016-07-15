### Jython ###
# see: http://www.jython.org/jythonbook/en/1.0/Concurrency.html#thread-safety
from __future__ import with_statement
from threading import Lock
# see: http://www.jython.org/archive/21/docs/jarray.html
from jarray import array


### Chairosoft ###
from chairosoft.util.function import consumer
from chairosoft.util.function import function
from chairosoft.jycycle_dealer import WebSocketObject
from chairosoft.jycycle_dealer import WebSocketObjectDelegate


### Jetty ###
# see: http://www.eclipse.org/jetty/download.html
# see: http://download.eclipse.org/jetty/9.2.17.v20160517/apidocs/
# see: http://download.eclipse.org/jetty/stable-9/xref/
from org.eclipse.jetty.server import Handler
from org.eclipse.jetty.server import Server

from org.eclipse.jetty.server.handler import ContextHandler
from org.eclipse.jetty.server.handler import ContextHandlerCollection
from org.eclipse.jetty.server.handler import DefaultHandler
from org.eclipse.jetty.server.handler import ResourceHandler

from org.eclipse.jetty.util.log import Log
#from org.eclipse.jetty.util.log import Logger

#from org.eclipse.jetty.websocket.api import RemoteEndpoint
#from org.eclipse.jetty.websocket.api import Session
from org.eclipse.jetty.websocket.api import WebSocketListener

from org.eclipse.jetty.websocket.server import WebSocketHandler

#from org.eclipse.jetty.websocket.servlet import ServletUpgradeRequest
#from org.eclipse.jetty.websocket.servlet import ServletUpgradeResponse
from org.eclipse.jetty.websocket.servlet import WebSocketCreator
#from org.eclipse.jetty.websocket.servlet import WebSocketServlet
#from org.eclipse.jetty.websocket.servlet import WebSocketServletFactory


### Java SE ###
# see: https://docs.oracle.com/javase/8/docs/api/
from java.lang import ClassLoader
from java.lang import String
from java.lang import System
from java.lang import Thread
from java.lang import Throwable

#from java.net import URLDecoder

from java.util import ArrayList
from java.util import Collections
from java.util import HashSet
#from java.util import List
#from java.util import Map
from java.util import Scanner
#from java.util import Set


#################
## Main Method ##
#################

def main():
    # see: http://www.eclipse.org/jetty/documentation/current/embedding-jetty.html
    server = Server(8080)
    
    rootHandler = ContextHandlerCollection()
    childHandlers = ArrayList()
    
    ## Web Sockets
    websocketContext = ContextHandler(rootHandler, "/wstest")
    websocketContext.setAllowNullPathInfo(True) # so "/wstest" is not redirected to "/wstest/"
    websocketHandler = TestWebSocketHandler()
    websocketContext.setHandler(websocketHandler)
    childHandlers.add(websocketContext)
    
    ## Files
    resourceContext = ContextHandler(rootHandler, "/")
    resourceHandler = ResourceHandler()
    resourceHandler.setDirectoriesListed(True)
    resourceHandler.setWelcomeFiles(array(["index.html"], String))
    resourceDirectory = getResourceDirectoryForModuleName(__name__)
    resourceHandler.setResourceBase(resourceDirectory)
    resourceContext.setHandler(resourceHandler)
    childHandlers.add(resourceContext)
    
    ## DefaultHandler
    childHandlers.add(DefaultHandler())
    
    rootHandler.setHandlers(array(childHandlers, Handler))
    server.setHandler(rootHandler)
    
    server.start()
    server.join()
#

def getResourceDirectoryForModuleName(moduleName):
    # serving from the "content" directory embedded in the JAR file
    prefix = "content/"
    moduleNamePath = moduleName.replace(".", "/")
    resourcePath = prefix + moduleNamePath
    resourceDirectory = ClassLoader.getSystemResource(resourcePath).toExternalForm()
    return resourceDirectory
#


#####################
## Websocket Stuff ##
#####################

class TestWebSocketHandler(WebSocketHandler):
    ## Instance Methods
    def configure(self, factory):
        factory.setCreator(TestWebSocketCreator())
    #
#

class TestWebSocketCreator(WebSocketCreator):
    ## Constructor
    def __init__(self):
        # Instance Fields
        self.testSocketDelegate = WebSocketObject(TestWebSocketDelegate())
    #
    
    ## Instance Methods
    def createWebSocket(self, req, resp):
        # Choose which sub-protocol to accept
        requestedSubProtocols = req.getSubProtocols()
        if requestedSubProtocols.size() > 0:
            acceptedSubProtocol = requestedSubProtocols.get(0)
            resp.setAcceptedSubProtocol(acceptedSubProtocol)
        #
        
        # Choose which web socket delegate to use for this request
        return self.testSocketDelegate
    #
#

class TestWebSocketDelegate(WebSocketObjectDelegate):
    ## Static Fields
    LOG = None
    SESSION_IDLE_TIMEOUT_MS = -1
    
    ## Constructor
    def __init__(self):
        # Instance Fields
        self.messageThread = TestMessageThread()
        
        # Initialization
        TestWebSocketDelegate.LOG.info("Created.")
        self.messageThread.start()
    #
    
    ## Instance Methods
    def handleWebSocketConnect(self, session):
        session.setIdleTimeout(TestWebSocketDelegate.SESSION_IDLE_TIMEOUT_MS)
        self.messageThread.addSession(session)
        TestWebSocketDelegate.LOG.info("Added session: " + str(session.hashCode()))
    #
    
    def handleWebSocketMessageString(self, session, text):
        TestWebSocketDelegate.LOG.info("WebSocket " + str(session.hashCode()) + " sent message: [" + text + "]")
    #
    
    def handleWebSocketError(self, session, error):
        TestWebSocketDelegate.LOG.warn("WebSocket " + str(session.hashCode()) + " error: " + str(error))
    #
    
    def handleWebSocketClose(self, session, statusCode, reason):
        self.messageThread.removeSession(session)
        TestWebSocketDelegate.LOG.info("Removed session: " + str(session.hashCode()))
    #
#
## TestWebSocketDelegate Static Init
TestWebSocketDelegate.LOG = Log.getLogger(TestWebSocketDelegate)

class TestMessageThread(Thread):
    ## Static Fields
    LOG = None
    
    ## Constructor
    def __init__(self):
        ## Instance Fields
        self.sessions = HashSet()
        self.sessionsLock = Lock()
        
        ## Initialization
        TestMessageThread.LOG.info("Created.")
    #
    
    ## Instance Methods
    def run(self):
        try:
            self.doRun()
        #
        except Throwable as ex:
            TestMessageThread.LOG.warn(ex.toString())
        #
        finally:
            TestMessageThread.LOG.info("Stopped.")
        #
    #
    
    def addSession(self, session):
        with self.sessionsLock:
            self.sessions.add(session)
        #
    #
    
    def removeSession(self, session):
        with self.sessionsLock:
            self.sessions.add(session)
        #
    #
    
    def doRun(self):
        jet = Scanner(System.in)
        while jet.hasNextLine():
            line = jet.nextLine()
            self.processLine(line)
        #
    #
    
    def processLine(self, line):
        with self.sessionsLock:
            self.sessions \
                .parallelStream() \
                .forEach(consumer(lambda session: self.relayLineToSession(line, session)))
        #
    #
    
    def relayLineToSession(self, line, session):
        try:
            if session.isOpen():
                remote = session.getRemote()
                remote.sendString(line)
            #
        #
        except Throwable as ex:
            TestMessageThread.LOG.warn("Problem while relaying message to " + str(session.hashCode()) + ": " + str(ex))
        #
    #
    
#
## TestMessageThread Static Init
TestMessageThread.LOG = Log.getLogger(TestMessageThread)


