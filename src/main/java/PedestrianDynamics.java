import engine.SimulationEngine;
import io.CsvFrameWriter;
import model.Parameters;
import model.SimulationState;

import java.nio.file.Files;
import java.nio.file.Paths;

public static void main(String[] args) throws Exception {
    int qIn = args.length > 0 ? Integer.parseInt(args[0]) : 4;
    int simulationTime = args.length > 1 ? Integer.parseInt(args[1]) : 60;//segundos

    Parameters p = Parameters.builder()
            .inflow(qIn)
            .build();

    SimulationEngine engine = new SimulationEngine(p, 20_000);

    Files.createDirectories(Paths.get("output"));
    double time=0;
    long tick=0;
    try (CsvFrameWriter writer = new CsvFrameWriter("output/run.csv", p.dt(), p.outputDt())) {
        while(time<simulationTime){
            SimulationState state = engine.step(tick,time);
            writer.writeFrameIfDue(state);
            time+=p.dt();
            tick++;
        }
    }
}
