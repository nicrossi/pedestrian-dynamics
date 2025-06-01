package model;

public record Particle(int id, Vector2D pos, Vector2D vel, double radius, int goalSign) {
    public Particle withPosition(Vector2D newPos) {
        return new Particle(id, newPos, vel, radius, goalSign);
    }

    public Particle withVelocity(Vector2D newVel) {
        return new Particle(id, pos, newVel, radius, goalSign);
    }

    public Particle withRadius(double newRadius) {
        return new Particle(id, pos, vel, newRadius, goalSign);
    }
}
