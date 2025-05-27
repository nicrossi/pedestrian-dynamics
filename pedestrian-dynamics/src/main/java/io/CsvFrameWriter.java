package io;

import java.io.BufferedWriter;

public class CsvFrameWriter {
    private final BufferedWriter bw;
    private final long dt;

    public CsvFrameWriter(BufferedWriter bw, long dt) {
        this.bw = bw;
        this.dt = dt;
    }

}
