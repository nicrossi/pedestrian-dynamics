package model;

public record Parameters(
        double vMax,
        double A_p, double B_p,
        double dt, double outputDt,
        double corridorLength, double corridorWidth,
        double inflowPerSide,
        double rMin, double rMax,
        double A_w, double B_w, double tau, double beta) {

    public static Builder builder() {
        return new Builder();
    }

    public static final class Builder {
        // TODO review these values!!
        private double A_w = 1215;
        private double B_w = 0.025;
        private double v = 1.5;
        private double A_p = 1.1, B_p = 2.1;

        private double L = 16, W = 3.6;
        private double inflow = 3.0;
        private double rMin = 0.10, rMax = 0.35;
        private double dt = 0.02;
        private double outDt = 5*dt;
        private final double tau = 0.5;
        private double beta = 0.9;

        public Builder beta(double beta) {
            this.beta = beta;
            return this;
        }

        public Builder desiredSpeed(double v0) {
            v = v0;
            return this;
        }

        public Builder Ap(double a) {
            A_p = a;
            return this;
        }

        public Builder Bp(double b) {
            B_p = b;
            return this;
        }

        public Builder dt(double d) {
            dt = d;
            return this;
        }

        public Builder outputDt(double d) {
            outDt = d;
            return this;
        }

        public Builder corridor(double len, double wid) {
            L = len;
            W = wid;
            return this;
        }

        public Builder inflow(double q) {
            inflow = q;
            return this;
        }

        public Builder rMin(double r) {
            rMin = r;
            return this;
        }

        public Builder rMax(double r) {
            rMax = r;
            return this;
        }

        public Builder Aw(double Aw) {
            A_w = Aw;
            return this;
        }

        public Builder Bw(double Bw) {
            B_w = Bw;
            return this;
        }

        public Parameters build() {
            return new Parameters(v, A_p, B_p, dt, outDt, L, W, inflow, rMin, rMax, A_w, B_w, tau, beta);
        }
    }
}
