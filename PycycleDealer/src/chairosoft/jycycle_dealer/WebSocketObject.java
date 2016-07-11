package chairosoft.jycycle_dealer;

import org.eclipse.jetty.websocket.api.Session;

import org.eclipse.jetty.websocket.api.annotations.OnWebSocketClose;
import org.eclipse.jetty.websocket.api.annotations.OnWebSocketConnect;
import org.eclipse.jetty.websocket.api.annotations.OnWebSocketError;
import org.eclipse.jetty.websocket.api.annotations.OnWebSocketFrame;
import org.eclipse.jetty.websocket.api.annotations.OnWebSocketMessage;
import org.eclipse.jetty.websocket.api.annotations.WebSocket;

@WebSocket
public class WebSocketObject
{
    // Instance Fields
    public final WebSocketObjectDelegate delegate;
    
    // Constructor
    public WebSocketObject(WebSocketObjectDelegate _delegate) 
    {
        this.delegate = _delegate;
    }
    
    // Instance Methods
    @OnWebSocketConnect
    public void onWebSocketConnect(Session session)
    {
        this.delegate.handleWebSocketConnect(session);
    }
    
    @OnWebSocketMessage
    public void onWebSocketMessageString(Session session, String text)
    {
        this.delegate.handleWebSocketMessageString(session, text);
    }
    
    @OnWebSocketError
    public void onWebSocketError(Session session, Throwable error)
    {
        this.delegate.handleWebSocketError(session, error);
    }
    
    @OnWebSocketClose
    public void onWebSocketClose(Session session, int statusCode, String reason)
    {
        this.delegate.handleWebSocketClose(session, statusCode, reason);
    }
}
