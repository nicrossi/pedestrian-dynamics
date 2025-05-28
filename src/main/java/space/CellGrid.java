package space;

import model.Vector2D;

import java.util.Arrays;
import java.util.function.IntConsumer;

public final class CellGrid {
    private final double cellSize;
    private final int cols, rows;
    // Flat array storing the head index of each cell (‑1 if empty).
    private final int[] head;
    // Next‑pointer for each particle (initial length maxAgents)
    private int[] next;

    public CellGrid(double W, double H, double cellSize, int N) {
        this.cellSize = cellSize;
        cols = (int) Math.ceil(W / cellSize);
        rows = (int) Math.ceil(H / cellSize);
        head = new int[cols * rows];
        next = new int[N];
        reset();
    }

    // Must be called once every tick before any insert.
    public void reset() {
        Arrays.fill(head, -1);
    }

    public void insert(int index, Vector2D position) {
        if (index >= next.length) {
            int newCap = Math.max(index + 1, next.length * 2);
            next = Arrays.copyOf(next, newCap);
        }
        int cell = getCellIndex(position);
        next[index] = head[cell];
        head[cell] = index;
    }

    /*
     * Iterates over all particles in the 3×3 surrounding 'position'.
     * 'IntConsumer' is invoked for each neighbor index.
     */
    public void forEachNeighbour(Vector2D position, IntConsumer consumer) {
        int cellX = (int) (position.x() / cellSize), cellY = (int) (position.y() / cellSize);
        for (int deltaY = -1; deltaY <= 1; deltaY++) {
            int neighborY = cellY + deltaY;
            if (neighborY < 0 || neighborY >= rows) {
                continue;
            }
            for (int deltaX = -1; deltaX <= 1; deltaX++) {
                int neighborX = cellX + deltaX;
                if (neighborX < 0 || neighborX >= cols) {
                    continue;
                }
                for (int agentIdx = head[neighborY * cols + neighborX]; agentIdx != -1; agentIdx = next[agentIdx]) {
                    consumer.accept(agentIdx);
                }
            }
        }
    }

    private int getCellIndex(Vector2D p) {
        int cx = Math.min(Math.max((int) (p.x() / cellSize), 0), cols - 1);
        int cy = Math.min(Math.max((int) (p.y() / cellSize), 0), rows - 1);
        return cy * cols + cx;
    }
}

