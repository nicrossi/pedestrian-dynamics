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


    @Override
    public Vector2D desiredDirection(Particle p_i, List<Particle> neighbors) {
        // Desired (target) direction e_t
        double goalSign = p_i.goalSign();
        Vector2D target = Vector2D.of(goalSign > 0 ? 16 : 0, p_i.pos().y());
        Vector2D e_t = target.sub(p_i.pos()).normalised();
        Vector2D sum_n_jc = Vector2D.zero();

        Vector2D v_i = p_i.vel();
        List<Particle> neighborsByDistance =neighbors.stream().filter(p->isFrontalParticle(p_i,p)).sorted(Comparator.comparingDouble(p->p.pos().distance(p_i.pos()))).toList();

        for (Particle p_j : neighborsByDistance.subList(0,Math.min(2,neighborsByDistance.size()))) {
            Vector2D r_ij = p_j.pos().sub(p_i.pos());
            double d = r_ij.length();
            if (d == 0.0) throw new ArithmeticException("Overlapping particles");

            Vector2D v_ij = p_j.vel().sub(v_i);
            Vector2D e_ij = p_i.pos().sub(p_j.pos()).normalised();
            double Beta = getAngle(v_ij,e_t);
            // Consider only frontal 180° (cos β < 0)
            Vector2D e_ij_c;
            if (v_ij.length()==0||Math.abs(Beta) <Math.PI/2) {
                e_ij_c = Vector2D.zero();
            }
            else {
                double dot = e_ij.dot(v_ij) / v_ij.length();
                double det = e_ij.cross(v_ij) / v_ij.length();
                double alpha = Math.atan2(det, dot);
                double fa = Math.abs(Math.abs(alpha) - Math.PI / 2);
                e_ij_c = e_ij.rotate(-Math.signum(alpha) * fa);
            }
            double w_j = A_p * Math.exp(-d / B_p);
            sum_n_jc=sum_n_jc.add(e_ij_c.mul(w_j));
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
    public boolean isFrontalParticle(Particle pi, Particle pj) {
        double x = pi.pos().x();
        boolean isGoingRight = pi.goalSign()==1;
        if (isGoingRight) {
            return pj.pos().x() >= x;
        }
        return pj.pos().x() <= x;
    }
    public double getAngle(Vector2D v,Vector2D u) {
        double dot = v.dot(u);
        double norm1 = u.length();
        double norm2 = v.length();
        double cos = Math.max(-1, Math.min(dot / (norm1 * norm2), 1));
        return Math.acos(cos);
    }
}
