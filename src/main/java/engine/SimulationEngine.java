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
    private final List<Integer> neighborIndices = new ArrayList<>();
    private final MovementStrategy movementStrategy;
    private final CellGrid grid;
    private int nextId = 0;
    private double countL = 0, countR = 0;

    public SimulationEngine(Parameters params, int maxParticles) {
        this.params = params;
        this.maxParticles = maxParticles;
        this.L = params.corridorLength();
        this.W = params.corridorWidth();
        this.movementStrategy = new AaCpmAvoidance(params.A_p(), params.B_p());
        this.grid = new CellGrid(L, W, params.rMax(), maxParticles); // TODO adjust to the appropriate cell size

    }

    public SimulationState step(long tick,double t) {
        spawn();
        removeExited();

        grid.reset();
        for (int i = 0; i < particles.size(); i++) {
            grid.insert(i, particles.get(i).pos());
        }

        List<Particle> next = new ArrayList<>(particles.size());

        for (int i = 0; i < particles.size(); i++) {
            Particle p = particles.get(i);
            List<Particle> neighbors = getNeighbors(i); // TODO

            p = p.withRadius(adjustRadius(p, neighbors,t));
            Vector2D dir = movementStrategy.desiredDirection(p, neighbors)
                    .add(wallForce(p.pos(), p.radius()))
                    .normalised();

            Vector2D velocity = dir.mul(params.desiredSpeed());
            Vector2D position = p.pos().add(velocity.mul(params.dt()));
            double y = Math.max(p.radius(), Math.min(W - 2 * p.radius(), position.y()));
            p = p.withPosition(Vector2D.of(position.x(), y)).withVelocity(velocity);
            next.add(p);
        }
        particles.clear();
        particles.addAll(next);

        return new SimulationState(tick, List.copyOf(next));
    }

    private double adjustRadius(Particle p, List<Particle> neighbors,double t) {
        for(Particle neighbour:neighbors){
            if(areColliding(p,neighbour))
                return params.rMin();
        }
        double r=p.radius();
        double dt=params.dt();
        return Math.min(params.rMax(), r * (t-dt) + params.rMax() * dt/params.tau());
    }

    private boolean areColliding(Particle p1,Particle p2){
        double ri=p1.radius();
        double rj=p2.radius();
        boolean radiiOverlap=p1.pos().distance(p2.pos())<ri+rj;
        boolean collide= ri == params.rMin() && radiiOverlap;
        Vector2D vi=p1.vel();
        Vector2D posDifference=p2.pos().sub(p1.pos());
        double betaAngle=Math.acos(vi.dot(posDifference)/(vi.length()*posDifference.length()));

        if(ri!=params.rMin()&& Math.toRadians(betaAngle)>-Math.PI/2 && Math.toRadians(betaAngle)<Math.PI/2 ){
            collide=true;
        }
        return collide && radiiOverlap && (lineProjectionIntersects(p1,p2));
    }

    private boolean lineProjectionIntersects(Particle p1, Particle p2) {
        // Approximate: project p1's velocity direction and see if it intersects p2's radius
        Vector2D dir = p1.vel().normalised();
        Vector2D leftEdge = p1.vel().add(dir.mul(params.rMin()));
        Vector2D rightEdge = p1.pos().add(dir.perpendicular().mul(-params.rMin()));

        double distToLeft = p2.pos().sub(leftEdge).length();
        double distToRight = p2.pos().sub(rightEdge).length();

        return (distToLeft < p2.radius() || distToRight < p2.radius());
    }

    private Vector2D wallForce(Vector2D p, double r) {
        double dBottom = p.y() - r;
        double dTop = (W - r) - p.y();
        Vector2D f = Vector2D.zero();
        if (dBottom < r)
            f = f.add(Vector2D.of(0, params.A_w() * Math.exp(-dBottom / params.B_w())));

        if (dTop < r)
            f = f.add(Vector2D.of(0, -params.A_w() * Math.exp(-dTop / params.B_w())));

        return f;
    }

    private List<Particle> getNeighbors(int idxSelf) {
        neighborIndices.clear();
        grid.forEachNeighbour(particles.get(idxSelf).pos(), j -> {
            if (j != idxSelf) {
                neighborIndices.add(j);
            }
        });
        List<Particle> result = new ArrayList<>(neighborIndices.size());
        for (int j : neighborIndices) result.add(particles.get(j));
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
    }

    private void spawnLeft() {
        if (particles.size() >= maxParticles) return;
        particles.add(initParticle(+params.desiredSpeed(), params.rMax()));
    }

    private void spawnRight() {
        if (particles.size() >= maxParticles) return;
        particles.add(initParticle(-params.desiredSpeed(), params.rMax()));
    }

    private Particle initParticle(double vx, double r) {
        double y = r + Math.random() * (W - 2 * r);
        double x = (vx > 0 ? -r : L + r);   // spawn just outside, slide in next tick
        return new Particle(nextId++, Vector2D.of(x, y), Vector2D.of(vx, 0), r);
    }

    private void removeExited() {
        particles.removeIf(p -> p.pos().x() < -p.radius() || p.pos().x() > L + p.radius());
    }

}
