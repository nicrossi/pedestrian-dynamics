package model;

public record Vector2D(double x, double y) {
    public static Vector2D of(double x, double y) {
        return new Vector2D(x, y);
    }

    public static Vector2D zero() {
        return new Vector2D(0.0, 0.0);
    }

    public Vector2D add(Vector2D o) {
        return new Vector2D(x + o.x, y + o.y);
    }

    public Vector2D sub(Vector2D o) {
        return new Vector2D(x - o.x, y - o.y);
    }

    public Vector2D mul(double scalar) {
        return new Vector2D(x * scalar, y * scalar);
    }
    public Vector2D perpendicular() {return new Vector2D(-y, x); } // 90-degree rotation}
    public double dot(Vector2D o) {
        return x * o.x + y * o.y;
    }

    public double cross(Vector2D o) {
        return x * o.y - y * o.x;
    }

    public double lengthSq() {
        return this.dot(this);
    }

    public double length() {
        return Math.sqrt(lengthSq());
    }

    public Vector2D normalised() {
        double len = length();
        return len == 0.0 ? this : new Vector2D(x / len, y / len);
    }

    public Vector2D rotate(double angle) {
        double cos = Math.cos(angle);
        double sin = Math.sin(angle);
        return new Vector2D(cos * x - sin * y, sin * x + cos * y);
    }

    public double distanceSq(Vector2D o) {
        return this.sub(o).lengthSq();
    }

    public double distance(Vector2D o) {
        return Math.sqrt(distanceSq(o));
    }
}
