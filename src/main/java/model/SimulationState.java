package model;

import java.util.List;

// Immutable snapshot of the simulation at a given tick.
public record SimulationState(long tick, List<Particle> particles,int pedestriansReached) {}