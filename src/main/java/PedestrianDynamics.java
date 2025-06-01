import engine.SimulationEngine;
import io.CsvFrameWriter;
import model.Parameters;
import model.SimulationState;

import java.nio.file.Files;
import java.nio.file.Paths;

public static void main(String[] args) throws Exception {
    int qIn = args.length > 0 ? Integer.parseInt(args[0]) : 1;
    int simulationTime = args.length > 1 ? Integer.parseInt(args[1]) : 120;//segundos

    Parameters p = Parameters.builder()
            .inflow(qIn)
            .build();

    SimulationEngine engine = new SimulationEngine(p, 20_000);

    Files.createDirectories(Paths.get("output"));
    double time=0;
    long tick=0;
    int pedestriansSpawnedLeft=0;
    int pedestriansSpawnedRight=0;
    String file_name = STR."output/run_\{qIn}.csv";
    try (CsvFrameWriter writer = new CsvFrameWriter(file_name, p.dt(), p.outputDt())) {
        while(pedestriansSpawnedLeft<100 || pedestriansSpawnedRight<100){
            SimulationState state = engine.step(tick,time);
            writer.writeFrameIfDue(state);
            time+=p.dt();
            tick++;
            pedestriansSpawnedLeft=state.pedestriansSpawnedLeft();
            pedestriansSpawnedRight=state.pedestriansSpawnedRight();
        }
    }
}
