package chairosoft.jycycle_dealer;

import org.python.util.PythonInterpreter;

public class PycycleDealerLauncher
{
    public static void main(String... args) throws Exception
    {
        PythonInterpreter interp = new PythonInterpreter();
        interp.exec("from chairosoft.pycycle_dealer import RoomServer");
        interp.exec("roomServer = RoomServer(8000)");
        interp.exec("roomServer.start()");
    }
}
