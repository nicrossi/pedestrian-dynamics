package engine;

import model.Particle;
import model.Vector2D;

import java.util.List;


/**
 * Anisotropic Adaptive Collision Potential Model (AA‑CPM).
 * Only neighbours with cos θ > 0 generate repulsion,
 * preventing the spurious attraction observed when cos θ < 0.
 */
public final class AaCpmAvoidance implements MovementStrategy {
    private final double A_p, B_p;

    public AaCpmAvoidance(double A, double B) {
        this.A_p = A;
        this.B_p = B;
    }

    @Override
    public Vector2D desiredDirection(Particle a, List<Particle> neighbors) {
        double sign = Math.signum(a.vel().x());
        if (sign == 0) {
            sign = 1;
        }
        // Always push forward
        Vector2D desiredDir = Vector2D.of(sign, 0);
        Vector2D acc = Vector2D.zero();

        for (Particle particle : neighbors) {
            if (particle.id() == a.id()) continue;

            Vector2D r = a.pos().sub(particle.pos());
            double dBetweenCenters = r.length();
            if (dBetweenCenters == 0) continue;

            Vector2D rVersor = r.normalised();
            double cos = rVersor.dot(desiredDir);
            if (cos >= 0) continue;  // skip neighbors behind

            double anis = -cos; // (0..1) front weighting
            // If 'separation' is positive, it indicates that the particles are not overlapping,
            // while a negative value suggests that the particles are intersecting.
            double separation = dBetweenCenters - a.radius() - particle.radius();
            double weight = A_p * Math.exp(-separation / B_p) * anis;
            acc = acc.add(rVersor.mul(weight));
        }

        Vector2D dir = desiredDir.add(acc).normalised();
        return dir.length() == 0 ? desiredDir : dir;
    }
}
