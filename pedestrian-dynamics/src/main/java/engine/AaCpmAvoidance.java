package engine;

import model.Particle;
import model.Vector2D;

import java.util.List;

public final class AaCpmAvoidance implements MovementStrategy {
    private final double A_p, B_p;
    public AaCpmAvoidance(double A, double B) {
        this.A_p = A;
        this.B_p = B;
    }

    @Override
    public Vector2D desiredDirection(Particle p, List<Particle> neighbors) {

        for (Particle particle : neighbors) {

        }
    }
}
