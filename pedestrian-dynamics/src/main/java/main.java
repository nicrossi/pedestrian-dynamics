import engine.SimulationEngine;
import io.CsvFrameWriter;
import model.Parameters;

public class main {
    public static void main(String[] args) throws Exception {
       int qIn = args.length > 0 ? Integer.parseInt(args[0]) : 4;
       int steps = args.length > 1 ? Integer.parseInt(args[1]) : 10_000;

        Parameters params = Parameters.builder()
                .inflowPerSide(qIn)
                .build();

        SimulationEngine engine = new SimulationEngine(params, 10_000);
    }
}
