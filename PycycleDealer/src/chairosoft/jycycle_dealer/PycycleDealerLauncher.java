package chairosoft.jycycle_dealer;

import org.python.util.PythonInterpreter;

public class PycycleDealerLauncher
{
    public static void main(String... args) throws Exception
    {
        PythonInterpreter interp = new PythonInterpreter();
        interp.exec("from chairosoft.websocket_test import main");
        interp.exec("main()");
    }
}
