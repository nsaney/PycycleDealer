package chairosoft.jycycle_dealer;

import org.eclipse.jetty.websocket.api.Session;

public interface WebSocketObjectDelegate
{
    void handleWebSocketConnect(Session session);
    void handleWebSocketMessageString(Session session, String text);
    void handleWebSocketError(Session session, Throwable error);
    void handleWebSocketClose(Session session, int statusCode, String reason);
}
