import engine.SimulationEngine;
import io.CsvFrameWriter;
import model.Parameters;
import model.SimulationState;

import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public static void main(String[] args) throws Exception {
    List<Double> timesQin4 = new ArrayList<>();
    List<Double> timesQin8 = new ArrayList<>();

    // Run same qIn range i times
    for (int i = 1; i <= 100; i++) {
        // Run many values for qIn
        for (int qIn = 4; qIn <= 8; qIn += 4) {
            Parameters p = Parameters.builder()
                    .inflow(qIn)
                    .outputDt(0.1)
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
            if (qIn == 4) {
                timesQin4.add(time);
            } else if (qIn == 8) {
                timesQin8.add(time);
            }
            System.out.println(STR."Simulation Time for qIn=\{qIn}, run=\{i}, finished in \{time} seconds. [Parameter: \{p}]");
        }
    }
    System.out.println(STR."Simulation for qIn=4, finished in \{Collections.min(timesQin4)} seconds.");
    System.out.println(STR."Simulation for qIn=8, finished in \{Collections.min(timesQin8)} seconds.");
}
