package engine;

import model.Parameters;
import model.Particle;
import model.SimulationState;
import model.Vector2D;
import space.CellGrid;

import java.util.ArrayList;
import java.util.List;

public final class SimulationEngine {
    private final Parameters params;
    private final int maxParticles;
    private final double L, W;
    private final List<Particle> particles = new ArrayList<>();
    private final MovementStrategy movementStrategy;
    private final CellGrid grid;


    public SimulationEngine(Parameters params, int maxParticles) {
        this.params = params;
        this.maxParticles = maxParticles;
        this.L = params.corridorLength();
        this.W = params.corridorWidth();
        this.movementStrategy = new AaCpmAvoidance(params.A_p(), params.B_p());
        this.grid = new CellGrid(/*...*/); // TODO initialize grid

    }

    public SimulationState step(long tick) {
        // TODO
        // spawn particles
        // remove particles that are out of bounds
        //
        List<Particle> next = new ArrayList<>(particles.size());
        for (int i = 0; i < particles.size(); i++) {
            Particle p = particles.get(i);
            List<Particle> neighbors = getNeighbors(i); // TODO
            // ajusto el radio?? // TODO
            p = p.withRadius(adjustRadius(p, neighbors));
            Vector2D dir = movementStrategy.desiredDirection(p, neighbors)
                    .add(wallForce(p.pos(), p.radius()))
                    .normalised();

            Vector2D velocity = dir.mul(params.desiredSpeed());
            Vector2D position = p.pos().add(velocity.mul(params.dt()));
            double y = Math.max(p.radius(), Math.min(W - p.radius(), position.y()));
            p = p.withPosition(Vector2D.of(position.x(), y)).withVelocity(velocity);
            // agrergaria lista
            next.add(p);
        }
        particles.clear();
        particles.addAll(next);

        return new SimulationState(tick, List.copyOf(next));
    }

    private double adjustRadius(Particle p, List<Particle> neighbors) {
        // TODO ni idea
        return 0;
    }

    private Vector2D wallForce(Vector2D p, double r) {
        double dBottom = p.y() - r;
        double dTop = (W - r) - p.y();
        Vector2D f = Vector2D.zero();
        if (dBottom < 1.0)
            f = f.add(Vector2D.of(0, params.A_w() * Math.exp(-dBottom / params.B_w())));

        if (dTop < 1.0)
            f = f.add(Vector2D.of(0, params.A_w() * Math.exp(-dTop / params.B_w())));

        return f;
    }


}
