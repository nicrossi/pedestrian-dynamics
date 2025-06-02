import engine.SimulationEngine;
import io.CsvFrameWriter;
import model.Parameters;
import model.SimulationState;

import java.nio.file.Files;
import java.nio.file.Paths;

public static void main(String[] args) throws Exception {

    // Run same qIn range i times
    for (int i = 1; i < 10; i++) {
        // Run many values for qIn
        for (int qIn = 1; qIn < 50; qIn += 5) {
            int simulationTime = args.length > 1 ? Integer.parseInt(args[1]) : 120;//segundos

            Parameters p = Parameters.builder()
                    .inflow(qIn)
                    .build();

            SimulationEngine engine = new SimulationEngine(p, 20_000);

            Files.createDirectories(Paths.get("output"));
            double time=0;
            long tick=0;
            String file_name = STR."output/run_\{qIn}_\{i}.csv";
            try (CsvFrameWriter writer = new CsvFrameWriter(file_name, p.dt(), p.outputDt())) {
                while(!engine.isFinished()){
                    SimulationState state = engine.step(tick,time);
                    writer.writeFrameIfDue(state);
                    time+=p.dt();
                    tick++;
                }
            }
        }
    }

}
