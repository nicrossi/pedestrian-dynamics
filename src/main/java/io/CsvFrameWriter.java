package io;

import model.Particle;
import model.SimulationState;
import model.Vector2D;

import java.io.BufferedWriter;
import java.io.Closeable;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;

/**
 * Writes selected frames of the simulation to a CSV file.
 */
public final class CsvFrameWriter implements Closeable {
    private final BufferedWriter bw;
    private final long dt2;
    private final double dt;
    private boolean skipHeader = false;

    public CsvFrameWriter(String path, double dt, double outputDt) throws IOException {
        this.bw = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(path), StandardCharsets.UTF_8));
        this.dt = dt;
        this.dt2 = Math.max(1, Math.round(outputDt / dt));
    }

    // Will write if
    public void writeFrameIfDue(SimulationState s) throws IOException {
        if (s.tick() % dt2 != 0) {
            return;
        }

        if (!skipHeader) {
            bw.write("time,id,x,y,vx,vy,radius");
            bw.newLine();
            skipHeader = true;
        }
        double timeSec = s.tick() * dt;
        for (Particle particle : s.particles()) {
            Vector2D p = particle.pos(), v = particle.vel();
            bw.write(timeSec + "," + particle.id() + "," + p.x() + "," + p.y() + "," + v.x() + "," + v.y() + "," + particle.radius());
            bw.newLine();
        }
    }

    @Override
    public void close() throws IOException {
        bw.close();
    }
}