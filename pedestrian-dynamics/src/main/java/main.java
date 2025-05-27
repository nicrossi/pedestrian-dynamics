import engine.SimulationEngine;
import io.CsvFrameWriter;
import model.Parameters;
import model.SimulationState;

public static void main(String[] args) throws Exception {
    int qIn = args.length > 0 ? Integer.parseInt(args[0]) : 4;
    int steps = args.length > 1 ? Integer.parseInt(args[1]) : 10_000;

    Parameters p = Parameters.builder()
            .inflow(qIn)
            .build();

    SimulationEngine engine = new SimulationEngine(p, 20_000);

    try (CsvFrameWriter writer = new CsvFrameWriter("run.csv", p.dt(), p.outputDt())) {
        for (long tick = 0; tick < steps; tick++) {
            SimulationState state = engine.step(tick);
            writer.writeFrameIfDue(state);
        }
    }
}
