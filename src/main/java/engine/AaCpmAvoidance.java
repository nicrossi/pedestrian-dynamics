package engine;

import model.Particle;
import model.Vector2D;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Vector;

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

    private record Neighbor(double dij, Vector2D wn) {}

    @Override
    public Vector2D desiredDirection(Particle p_i, List<Particle> neighbors) {
        // Desired (target) direction e_t
        double goalSign = p_i.goalSign();
        Vector2D target = Vector2D.of(goalSign > 0 ? 16 : 0, p_i.pos().y());
        Vector2D e_t = target.sub(p_i.pos()).normalised();
        Vector2D sum_n_jc = Vector2D.zero();

        Vector2D v_i = p_i.vel();
        List<Neighbor> frontNeighbors = new ArrayList<>(5);

        for (Particle p_j : neighbors) {
            if (p_j.id() == p_i.id()) continue;
            Vector2D r_ij = p_j.pos().sub(p_i.pos());
            double d = r_ij.length();
            if (d == 0.0) continue;
            // v_i · r_ij ≥ 0
            if (v_i.lengthSq() > 0 && v_i.dot(r_ij) / (v_i.length() * d) < 0.0) continue;

            Vector2D v_ij = p_j.vel().sub(v_i);
            Vector2D e_ij = p_i.pos().sub(p_j.pos()).normalised();
            double cosBeta = v_ij.length() == 0 ? 0 : v_ij.dot(e_t) / v_ij.length();
            // Consider only frontal 180° (cos β < 0)
            if (cosBeta >= 0.0 || Double.isNaN(cosBeta)) continue;

            double dot=e_ij.dot(v_ij)/v_ij.length();
            double det= e_ij.cross(v_ij)/v_ij.length();
            double alpha =Math.atan2(det,dot);
            double fa = Math.abs(Math.abs(alpha) - Math.PI / 2);
            Vector2D e_ij_c = e_ij.rotate(-Math.signum(alpha)* fa);
//            System.out.printf("cosBeta: %f, alpha: %f, fa: %f\n", cosBeta, alpha, fa);
            double w_j = A_p * Math.exp(-d / B_p);
            frontNeighbors.add(new Neighbor(d, e_ij_c.mul(w_j)));
        }
        frontNeighbors.sort(Comparator.comparingDouble(Neighbor::dij));
        for (int k=0; k < Math.min(2, frontNeighbors.size()); k++) {
            sum_n_jc = sum_n_jc.add(frontNeighbors.get(k).wn());
        }

        // Wall repulsion n_wc
        double dBottom = p_i.pos().y();
        boolean closerToBottom = dBottom < W - dBottom;
        Vector2D w = Vector2D.of(p_i.pos().x(), closerToBottom ? 0.0 : W);
        Vector2D ei_w = w.sub(p_i.pos()).normalised();
        double d_iw = closerToBottom ? dBottom : W - dBottom;
        Vector2D n_wc = ei_w.mul(A_w * Math.exp(-d_iw / B_w));

        return e_t.add(sum_n_jc).add(n_wc).normalised(); // e_a
    }
}
