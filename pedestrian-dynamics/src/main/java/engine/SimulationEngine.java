package engine;

import model.Parameters;
import model.Particle;
import model.Vector2D;

import java.util.ArrayList;
import java.util.List;

public final class SimulationEngine {
    private final Parameters params;
    private final int maxParticles;
    private final double L, W;
    private final List<Particle> particles = new ArrayList<>();
    private final MovementStrategy movementStrategy;
    private static final double A_W = 10.0;
    private static final double B_W = 1.0;

    public SimulationEngine(Parameters params, int maxParticles) {
        this.params = params;
        this.maxParticles = maxParticles;
        this.L = params.corridorLength();
        this.W = params.corridorWidth();
        this.movementStrategy = new AaCpmAvoidance(params.A_p(), params.B_p());
    }

    // step()
        // inyecte particulas
        // remueva las que salen

        // por cada particula
            // get neighbors

    public void step(long tick) {
        // agregar particulas
        for (int i = 0; i < particles.size(); i++) {
            Particle p = particles.get(i);
            List<Particle> neighbors = getNeighbors(); // TODO
            // ajusto el radio?? // TODO
            p = p.withRadius(adjustRadius(p, neighbors));
            Vector2D dir = movementStrategy.desiredDirection(p, neighbors)
                    .normalized();

            Vector2D velocity = dir.mul(params.desiredSpeed());
            Vector2D position = p.pos().add(velocity.mul(params.dt()));
            double y = Math.max(p.radius(), Math.min(W - p.radius(), position.y()));
            p = p.withPosition(Vector2D.of(position.x(), y)).withVelocity(velocity);
            // agrergaria lista
        }
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
            f = f.add(Vector2D.of(0, A_W * Math.exp(-dBottom / B_W)));

        if (dTop < 1.0)
            f = f.add(Vector2D.of(0, A_W * Math.exp(-dTop / B_W)));

        return f;
    }


}
