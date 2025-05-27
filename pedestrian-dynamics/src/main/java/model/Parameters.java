package model;

public record Parameters(
        double desiredSpeed,
        double A_p, double B_p,
        double dt, double outputDt,
        double corridorLength, double corridorWidth,
        double rMin, double rMax,
        double inflowPerSide) {

    public static Builder builder() { return new Builder(); }

    public static final class Builder {
        private double v = 1.5;
        // TODO add the rest

    }
}
