package model;

public record Particle(int id, Vector2D pos, Vector2D vel, double radius) {
    public Particle withPosition(Vector2D newPos) {
        return new Particle(id, newPos, vel, radius);
    }

    public Particle withVelocity(Vector2D newVel) {
        return new Particle(id, pos, newVel, radius);
    }

    public Particle withRadius(double newRadius) {
        return new Particle(id, pos, vel, newRadius);
    }
}
