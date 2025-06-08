package engine;

import model.Parameters;
import model.Particle;
import model.SimulationState;
import model.Vector2D;
import space.CellGrid;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

public final class SimulationEngine {
    private static final int LEFT = 0;
    private static final int RIGHT = 16;
    private final Parameters params;
    private final int maxParticles;
    private final double L, W;
    private final List<Particle> particles = new ArrayList<>();
    private final List<Integer> neighborIndices = new ArrayList<>();
    private final MovementStrategy movementStrategy;
    private final CellGrid grid;
    private int nextId = 0;
    private double countL = 0, countR = 0;
    private int pedestriansSpawnedLeft = 0;
    private int pedestriansSpawnedRight = 0;
    private int pedestriansExitLeft = 0;
    private int pedestriansExitRight = 0;

    public SimulationEngine(Parameters params, int maxParticles) {
        this.params = params;
        this.maxParticles = maxParticles;
        this.L = params.corridorLength();
        this.W = params.corridorWidth();
        this.movementStrategy = new AaCpmAvoidance(params.A_p(), params.B_p(), params.A_w(), params.B_w(), params.corridorWidth());
        this.grid = new CellGrid(L, W, params.rMax(), maxParticles);

    }

    public SimulationState step(long tick, double t) {
        spawn();
        removeExited();

        System.out.printf("tick %d  size=%d  exitedL=%d exitedR=%d rMin-count=%d\n",
                tick, particles.size(), pedestriansExitLeft, pedestriansExitRight,
                particles.stream().filter(pp -> pp.radius() == params.rMin()).count());

        grid.reset();
        for (int i = 0; i < particles.size(); i++) {
            grid.insert(i, particles.get(i).pos());
        }

        List<Particle> next = new ArrayList<>(particles.size());

        for (int i = 0; i < particles.size(); i++) {
            Particle p = particles.get(i);
            List<Particle> neighbors = getNeighbors(i);
            double rNew = adjustRadius(p, neighbors);
            boolean inContact = (rNew == params.rMin());

            Vector2D dir;
            double speed;

            if (inContact) {
                /* 3.2a contact mode — choose e_ij of *nearest* colliding neighbour */
                Particle nearest = null;
                double minDist = Double.POSITIVE_INFINITY;
                for (Particle n : neighbors) {
                    if (areColliding(p.withRadius(rNew), n)) {
                        double d = n.pos().sub(p.pos()).lengthSq();
                        if (d < minDist) {
                            minDist = d;
                            nearest = n;
                        }
                    }
                }
                if (nearest == null) {
                    // numerical fall‑back (should not happen): treat as free mode
                    dir = movementStrategy.desiredDirection(p.withRadius(rNew), neighbors);
                    speed = freeSpeed(rNew);
                } else {
                    dir = p.pos().sub(nearest.pos()).normalised();
                    speed = params.vMax();
                }
            } else {
                /* 3.2b free mode */
                dir = movementStrategy.desiredDirection(p.withRadius(rNew), neighbors);
                speed = freeSpeed(rNew);
            }


            Vector2D vel = dir.mul(speed);
            Vector2D pos = p.pos().add(vel.mul(params.dt()));
            double x = p.goalSign() > 0 ? Math.max(rNew, pos.x()) : Math.min(L - rNew, pos.x());
            double y = Math.max(rNew, Math.min(W - rNew, pos.y()));

            Particle pNext = p.withPosition(Vector2D.of(x, y))
                    .withVelocity(vel)
                    .withRadius(rNew);
            next.add(pNext);
        }
        particles.clear();
        particles.addAll(next);

        return new SimulationState(tick, List.copyOf(next), pedestriansSpawnedLeft, pedestriansSpawnedRight);
    }

    private double adjustRadius(Particle p, List<Particle> neighbors) {
        for (Particle neighbour : neighbors) {
            if (areColliding(p, neighbour)) {
                return params.rMin();
            }
        }
        double r = p.radius();
        double dr = (params.rMax() - r) * params.dt() / params.tau();
        double rNew = r + dr;
        return Math.min(params.rMax(), Math.max(params.rMin(), rNew));
    }

    private double freeSpeed(double r) {
        double alpha = (r - params.rMin()) / (params.rMax() - params.rMin());
        return params.vMax() * Math.pow(Math.max(0.0, alpha), params.beta());
    }

    /**
     * Contact criterion (paper §3.1):
     * – If r_i = r_min: contact ⇔ radii overlap.
     * – Else: (i) frontal sector (−π/2 < β < π/2),
     * (ii) radii overlap, and
     * (iii) the circle j intersects the strip delimited by the two
     * lines parallel to v_i and tangent to the circle of radius r_min
     * centred at i.
     */
    private boolean areColliding(Particle p_i, Particle p_j) {
        double r_i = p_i.radius();
        double r_j = p_j.radius();
        double r_min = params.rMin();

        /* Distance and overlap test */
        Vector2D r_ij = p_j.pos().sub(p_i.pos());
        double d_centres = r_ij.length();
        boolean radiiOverlap = d_centres < (r_i + r_j);

        /* Case r_i = r_min ⇒ only overlap required (bullet 1) */
        if (r_i == r_min) {
            return radiiOverlap;
        }

        /* Signed angle β between v_i and r_ij (bullet 2) */
        Vector2D v_i = p_i.vel();
        if (v_i.lengthSq() == 0.0) {
            return false; // static agent
        }

        double beta = Math.atan2(v_i.cross(r_ij), v_i.dot(r_ij));
        boolean frontal = beta > -Math.PI / 2 && beta < Math.PI / 2;

        /* Tangential-strip intersection (bullet 3) */
        boolean stripIntersect = intersectsTangentialStrip(p_i, p_j);

        return frontal && radiiOverlap && stripIntersect;
    }

    /**
     * Returns true if the circle centred at j intersects either of the two
     * lines that are parallel to v_i and tangent to the auxiliary circle of
     * radius r_min around i (paper Fig. 1, right panel).
     */
    private boolean intersectsTangentialStrip(Particle p_i, Particle p_j) {
        double r_min = params.rMin();
        Vector2D v_i = p_i.vel();
        if (v_i.lengthSq() == 0.0) {
            return false; // no heading ⇒ no strip
        }

        /* Unit vectors along and perpendicular to v_i */
        Vector2D dir = v_i.normalised();
        Vector2D perp = dir.perpendicular();

        /* Points on the two tangent lines */
        Vector2D leftPt = p_i.pos().add(perp.mul(r_min));
        Vector2D rightPt = p_i.pos().sub(perp.mul(r_min));

        /* Signed distances from p_j to each line (|perp·(p - a)|) */
        double distLeft = Math.abs(perp.dot(p_j.pos().sub(leftPt)));
        double distRight = Math.abs(perp.dot(p_j.pos().sub(rightPt)));

        return distLeft < p_j.radius() || distRight < p_j.radius();
    }


    private List<Particle> getNeighbors(int idxSelf) {
        neighborIndices.clear();
        grid.forEachNeighbour(particles.get(idxSelf).pos(), j -> {
            if (j != idxSelf) {
                neighborIndices.add(j);
            }
        });
        List<Particle> result = new ArrayList<>(neighborIndices.size());
        for (int j : neighborIndices) {
            result.add(particles.get(j));
        }
        return result;
    }

    private void spawn() {
        // Calculate the expected number of particles to spawn per side this tick
        double inflowPerTick = params.inflowPerSide() * params.dt();
        countL += inflowPerTick;
        countR += inflowPerTick;

        int spawnLeftCount = (int) countL;
        countL -= spawnLeftCount;
        for (int i = 0; i < spawnLeftCount; i++) {
            spawnLeft();
        }

        int spawnRightCount = (int) countR;
        countR -= spawnRightCount;
        for (int i = 0; i < spawnRightCount; i++) {
            spawnRight();
        }
        pedestriansSpawnedRight += spawnRightCount;
        pedestriansSpawnedLeft += spawnLeftCount;
    }

    private void spawnLeft() {
        if (particles.size() >= maxParticles) {
            return;
        }
        particles.add(initParticle(+params.vMax(), params.rMin(), LEFT));
    }

    private void spawnRight() {
        if (particles.size() >= maxParticles) {
            return;
        }
        particles.add(initParticle(-params.vMax(), params.rMin(), RIGHT));
    }

    private Particle initParticle(double vx, double r, int begin) {
        double y = r + Math.random() * (W - 2 * r);
        double x = (vx > 0 ? -r : L + r);   // spawn just outside, slide in next tick
        int goalSign = vx > 0 ? 1 : -1;
        return new Particle(nextId++, Vector2D.of(x, y), Vector2D.of(vx, 0), r, goalSign, begin);
    }

    private void removeExited() {
        Iterator<Particle> it = particles.iterator();
        while (it.hasNext()) {
            Particle p = it.next();
            if (p.begin() == LEFT && p.pos().x() > L || p.begin() == RIGHT && p.pos().x() < 1 - p.radius()) {
                it.remove();
                if (p.begin() == LEFT) {
                    pedestriansExitLeft++;
                }
                if (p.begin() == RIGHT) {
                    pedestriansExitRight++;
                }

            }
        }
    }

    public boolean isFinished() {
        return pedestriansExitRight >= 100 && pedestriansExitLeft >= 100;
    }
}
