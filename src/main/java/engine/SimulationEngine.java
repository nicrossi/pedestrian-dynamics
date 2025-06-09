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
        this.grid = new CellGrid(L, W, 1.1 * params.rMax(), maxParticles);

    }

    public SimulationState step(long tick, double t) {
        spawn();
        removeExited();

        System.out.printf("Qin: %f, tick %d  size=%d  exitedL=%d exitedR=%d rMin-count=%d\n",
                params.inflowPerSide(), tick, particles.size(), pedestriansExitLeft, pedestriansExitRight,
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
            boolean inContact = (p.radius() == params.rMin());

            Vector2D dir;
            double speed;

            if (inContact) {
                Vector2D sum = Vector2D.zero();
                for (Particle n : neighbors) {
                    if (p.id() == n.id()) continue;

                    if (areColliding(p, n)) {
                        sum = sum.add(p.pos().sub(n.pos()).normalised());
                    }
                }
                dir = sum.normalised();
                speed = params.vMax();
            } else {
                dir = movementStrategy.desiredDirection(p, neighbors);
                speed = freeSpeed(p.radius());
            }

            Vector2D vel = dir.mul(speed);
            Vector2D pos = p.pos().add(vel.mul(params.dt()));
            double x = p.goalSign() > 0 ? Math.max(p.radius(), pos.x()) : Math.min(L - p.radius(), pos.x());
            double y = Math.max(p.radius(), Math.min(W - p.radius(), pos.y()));

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
        double r =p.radius();
        return Math.min(r+params.rMax()*params.dt()/params.tau(),params.rMax());
    }

    private double freeSpeed(double r) {
        double alpha = (r - params.rMin()) / (params.rMax() - params.rMin());
        return params.vMax() * Math.pow(Math.max(0.0, alpha), params.beta());
    }

    private boolean areColliding(Particle p_i, Particle p_j) {

        double r_min = params.rMin();
        Vector2D r_ij=p_j.pos().sub(p_i.pos());
        boolean radiiOverlap=r_ij.length() < p_i.radius()+p_j.radius();
        boolean firstCondition=p_i.radius()==r_min && radiiOverlap;

        Vector2D vel=p_i.vel();
        double cosBeta=r_ij.dot(vel)/(vel.length()*r_ij.length());
        if(p_i.radius()!=r_min && cosBeta>=0){
            firstCondition=true;
        }

        return firstCondition && radiiOverlap && intersectsTangentialStrip(p_i,p_j);
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
            return false; // No heading ⇒ no strip
        }

        Vector2D dir = v_i.normalised();
        Vector2D perp = dir.perpendicular();

        Vector2D diff = p_j.pos().sub(p_i.pos());

        // Check if j is in front of i
        double forward = dir.dot(diff);
        if (forward < 0) return false;

        double dist = Math.abs(perp.dot(diff));

        return dist < r_min + p_j.radius();
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
            if (p.begin() == LEFT && p.pos().x() > L
                    || p.begin() == RIGHT && p.pos().x() < 0) {
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
