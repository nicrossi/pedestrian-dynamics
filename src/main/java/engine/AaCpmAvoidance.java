package engine;

import model.Particle;
import model.Vector2D;

import java.util.List;

public final class AaCpmAvoidance implements MovementStrategy {
    private final double A_p, B_p;
    private final double A_w, B_w;
    private final double W;

    public AaCpmAvoidance(double A_p, double B_p, double A_w, double B_w, double W) {
        this.A_p = A_p;
        this.B_p = B_p;
        this.A_w = A_w;
        this.B_w = B_w;
        this.W = W;
    }

    @Override
    public Vector2D desiredDirection(Particle p_i, List<Particle> neighbours) {
        // Desired (target) direction e_t
        double goalSign = p_i.goalSign();
        Vector2D e_t = Vector2D.of(goalSign, 0.0);
        // Σ n_jc : weighted sum of pairwise collision vectors
        Vector2D sum_n_jc = Vector2D.zero();

        for (Particle p_j : neighbours) {
            if (p_j.id() == p_i.id()) continue;
            // Vector j->i
            Vector2D r_ji = p_i.pos().sub(p_j.pos());
            // Distance between centers
            double d = r_ji.length();
            if (d == 0.0) continue;

            Vector2D e_ji = r_ji.normalised(); // unit collision dir
            double cosBeta = e_ji.dot(e_t);    // β between e_ji & e_t

            // Consider only frontal 180° (cos β < 0)
            if (cosBeta >= 0.0) continue;

            // Separation distance between outlines (negative ⇒ overlap)
            double d_sep = d - p_i.radius() - p_j.radius();
            // Weight w_j (Eq.6) : A_p exp(−d_sep/B_p) (−cos β)
            double w_j = A_p * Math.exp(-d_sep / B_p) * (-cosBeta);
            // Contribution to Σ n_jc
            sum_n_jc = sum_n_jc.add(e_ji.mul(w_j));
        }

        // Wall repulsion n_wc
        double d_bottom = p_i.pos().y() - p_i.radius();
        double d_top = (W - p_i.radius() - p_i.pos().y());
        Vector2D n_wc = Vector2D.of(0.0,
                A_w * Math.exp(-d_bottom / B_w) - A_w * Math.exp(-d_top / B_w));

        // Here we just form e_a = (e_t + Σ n_jc)̂  (Eq.6)
        Vector2D e_a_raw = e_t.add(sum_n_jc).add(n_wc);

        Vector2D e_a = e_a_raw.normalised();
        // Prevent reversing (always move toward goal)
        if (Math.signum(e_a.x()) != p_i.goalSign()) {
            //System.out.println("=== SIGN CHANGE ===");
           // e_a = Vector2D.of(-e_a.x(), e_a.y());
        }

        return e_a;
    }
}
