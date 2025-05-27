package engine;

import model.Particle;
import model.Vector2D;

import java.util.List;

public interface MovementStrategy {
    Vector2D desiredDirection(Particle particle, List<Particle> neighbors);
}
